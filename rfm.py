# RFM ile Müşteri Segmentasyonu (Customer Segmentation with RFM)
# 1. İş Problemi (Business Problem)
# 2. Veriyi Anlama (Data Understanding)
# 3. Veri Hazırlama (Data Preparation)
# 4. RFM Metriklerinin Hesaplanması (Calculating RFM Metrics)
# 5. RFM Skorlarının Hesaplanması (Calculating RFM Scores)
# 6. RFM Segmentlerinin Oluşturulması ve Analiz Edilmesi (Creating & Analysing RFM Segments)
# 7. Tüm Sürecin Fonksiyonlaştırılması


# 1. İş Problemi (Business Problem)
# Bir e-ticaret şirketi müşterilerini segmentlere ayırıp bu segmentlere göre
# pazarlama stratejileri belirlemek istiyor.
# Veri Seti Hikayesi
# https://archive.ics.uci.edu/ml/datasets/Online+Retail+II

# Online Retail II isimli veri seti İngiltere merkezli online bir satış mağazasının
# 01/12/2009 - 09/12/2011 tarihleri arasındaki satışlarını içeriyor.
# Değişkenler
#
# InvoiceNo: Fatura numarası. Her işleme yani faturaya ait eşsiz numara. C ile başlıyorsa iptal edilen işlem.
# StockCode: Ürün kodu. Her bir ürün için eşsiz numara.
# Description: Ürün ismi
# Quantity: Ürün adedi. Faturalardaki ürünlerden kaçar tane satıldığını ifade etmektedir.
# InvoiceDate: Fatura tarihi ve zamanı.
# UnitPrice: Ürün fiyatı (Sterlin cinsinden)
# CustomerID: Eşsiz müşteri numarası
# Country: Ülke ismi. Müşterinin yaşadığı ülke.

# 2. Veriyi Anlama (Data Understanding)
import pandas as pd
import datetime as dt
pd.set_option("display.max_columns", None)
pd.set_option("display.float_format", lambda x: '%.3f' % x)
df_=pd.read_excel("C:/Users/asus/Desktop/miuul/online_retail_II.xlsx", sheet_name="Year 2009-2010")
df=df_.copy()
df.head()
df.shape
df.isnull().sum()
# essiz urun sayisi nedir?
df["Description"].nunique()
#herbir üründen kaçar tane var(kaçar tane satılmış)?
df["Description"].value_counts()
#en çok sipariş edilen ürün hangisidir?
df.groupby("Description").agg({'Quantity': 'sum'}).head()
#yukarıdaki sonuç hatalı çıktı. Bu kısım veri ön işleme bölümünde ele alınacak.Her bir üründen toplamda ne kadar sipariş verildiğini görmek için:
df.groupby("Description").agg({"Quantity": "sum"}).sort_values("Quantity", ascending=False).head()
#toplam kaç tane fatura kesilmiş?
df["Invoice"].nunique()
#fatura başına toplam ne kadar kazanılmıştır? Bu işlem için önce ürünün toplam fiyatı hesaplanır:
df["Total Price"] = df["Quantity"] * df["Price"]
#fatura başına toplam kazanç için:
df.groupby("Invoice").agg({'Total Price': 'sum'}).head()

# 3. Veri Hazırlama (Data Preparation)
df.shape
df.isnull().sum()
#boş değerleri silmek için:
df.dropna(inplace=True)
#faturalarda (invoice) 'c' harfi ile başlayanlar iadeleri ifade etmektedir. Bu da veriyi anlama bölümünde karşımıza çıkan hatalı değerlere (-) sebep olmaktadır. Görmek için:
df.describe().T
#iade edilen faturaları veri setinden çıkarmak için:
df = df[~df["Invoice"].str.contains('C', na=False)]

# 4. RFM Metriklerinin Hesaplanması (Calculating RFM Metrics)
# Recency, Frequency, Monetary
#Recency: Analizin yapıldığı tarih - ilgili müşterinin son satın alım tarihi
#Frequency: Müşterinin yaptığı toplam satın alma
#Monetary: Müşterinin yaptığı toplam satın almalar neticesinde bıraktığı toplam parasal değerdir.

#Analizin yapıldığı tarihi belirlemek için son tarihin üzerine örneğin 2 gün ekleyerek bu tarihi analiz yapılan tarih olarak kabul edebiliriz.
df['InvoiceDate'].max()
today_date = dt.datetime(2010, 12, 11)
type(today_date)

#rfm analizi için
rfm = df.groupby('Customer ID').agg({'InvoiceDate': lambda InvoiceDate: (today_date - InvoiceDate.max()).days,
                                     'Invoice': lambda Invoice: Invoice.nunique(),
                                     'Total Price': lambda TotalPrice: TotalPrice.sum()})
rfm.head()
rfm.columns = ['recency','frequency', 'monetary']
rfm.describe().T
rfm = rfm[rfm["monetary"] > 0]

# 5. RFM Skorlarının Hesaplanması (Calculating RFM Scores)
#recency değerinde küçük olanlar 5 puan, qcut ile çeyrek değerlere göre sıralar. qcut Küçükten büyüğe sıralar ve belirli parçalara göre böler.
rfm["recency score"] = pd.qcut(rfm['recency'], 5, labels=[5,4,3,2,1])

#monetary
rfm['monetary score'] = pd.qcut(rfm['monetary'], 5, labels=[1,2,3,4,5])

#frequency
rfm['frequency score'] = pd.qcut(rfm['frequency'].rank(method="first"), 5, labels=[1,2,3,4,5])

#rfm skorunu oluiturmak için recency ve frequency değerleri string olarak yan yana yazılır:
rfm["RFM_SCORE"]=(rfm['recency score'].astype(str) +
                  rfm['frequency score'].astype(str))
#örneğin champion müşterileri görmek için:
rfm[rfm["RFM_SCORE"] == "55"]

# 6. RFM Segmentlerinin Oluşturulması ve Analiz Edilmesi (Creating & Analysing RFM Segments)
# regex (Regular Expression)

# RFM isimlendirmesi
seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}
rfm['segment'] = rfm["RFM_SCORE"].replace(seg_map, regex=True)


rfm[["segment", "recency", "frequency", "monetary"]].groupby("segment").agg(["mean", "count"])

#örneğin can't loose müşterilerin bilgilerine ve idlerine erişmek istersek:
rfm[rfm["segment"] == "cant_loose"].head()
rfm[rfm["segment"] == "cant_loose"].index
#bunları yeni bir dataframe'e eklemek için:
new_df = pd.DataFrame()
new_df["new_customer_id"] = new_df["new_customer_id"].astype(int) #idleri int yaptık
new_df["new_customer_id"] = rfm[rfm["segment"] == "new_customers"].index
new_df.to_csv("new_customers.csv")
#rfm verilerinin hepsini csc dosyası olarak çıkarmak için
rfm.to_csv("rfm.csv")

# 7. Tüm Sürecin Fonksiyonlaştırılması
def create_rfm(dataframe, csv=False):

    # VERIYI HAZIRLAMA
    dataframe["TotalPrice"] = dataframe["Quantity"] * dataframe["Price"]
    dataframe.dropna(inplace=True)
    dataframe = dataframe[~dataframe["Invoice"].str.contains("C", na=False)]

    # RFM METRIKLERININ HESAPLANMASI
    today_date = dt.datetime(2011, 12, 11)
    rfm = dataframe.groupby('Customer ID').agg({'InvoiceDate': lambda date: (today_date - date.max()).days,
                                                'Invoice': lambda num: num.nunique(),
                                                "TotalPrice": lambda price: price.sum()})
    rfm.columns = ['recency', 'frequency', "monetary"]
    rfm = rfm[(rfm['monetary'] > 0)]

    # RFM SKORLARININ HESAPLANMASI
    rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
    rfm["frequency_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
    rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])

    # cltv_df skorları kategorik değere dönüştürülüp df'e eklendi
    rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) +
                        rfm['frequency_score'].astype(str))


    # SEGMENTLERIN ISIMLENDIRILMESI
    seg_map = {
        r'[1-2][1-2]': 'hibernating',
        r'[1-2][3-4]': 'at_risk',
        r'[1-2]5': 'cant_loose',
        r'3[1-2]': 'about_to_sleep',
        r'33': 'need_attention',
        r'[3-4][4-5]': 'loyal_customers',
        r'41': 'promising',
        r'51': 'new_customers',
        r'[4-5][2-3]': 'potential_loyalists',
        r'5[4-5]': 'champions'
    }

    rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)
    rfm = rfm[["recency", "frequency", "monetary", "segment"]]
    rfm.index = rfm.index.astype(int)

    if csv:
        rfm.to_csv("rfm.csv")

    return rfm

df = df_.copy()

rfm_new = create_rfm(df, csv=True)

