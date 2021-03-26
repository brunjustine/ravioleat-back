RESTAURANT = {
    "Api": str,
    "Id": int,
    "Name": str,
    "UniqueName": str,
    "Address": {
       "City": str,
       "FirstLine": str,
       "Postcode": str,
       "Latitude": float,
       "Longitude": float
    },
    "Rating": {
       "Count": str,
       "StarRating": float
    },
    "Description": str,
    "Url": str,
    "LogoUrl": str,
    "DeliveryEtaMinutes": {
       "RangeLower": int,
       "RangeUpper": int
    },
    "IsOpenNow": bool,
    "DeliveryCost": float,
    "Offers": [
        {
            "Description": str,
            "OfferId": int
        }
    ],
    "CuisineTypes": [
       {
           "Id": int,
           "Name": str,
           "SeoName": str
       }
    ],
    "PriceCategory": int,
}