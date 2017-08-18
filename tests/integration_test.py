import bottlenose

from utils import AMAZON_ASSOCIATE_TAG, AMAZON_REGION


def test_bottlenose():
    '''
    Tests integration with bottlenose.
    bottlenose.Amazon.ItemSearch() should return an XML containing the response
    '''
    amazon = bottlenose.Amazon(AssociateTag=AMAZON_ASSOCIATE_TAG, Region=AMAZON_REGION)
    product = {"keywords": "magic"}
    response = amazon.ItemSearch(Keywords=product['keywords'], SearchIndex='All', ResponseGroup='Medium')
    assert str(response).find('<ItemSearchResponse') > 0
