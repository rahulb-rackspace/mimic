from mimic.model import cloudfeeds
from twisted.trial.unittest import SynchronousTestCase
from testtools.matchers import (MatchesSetwise, MatchesDict, Equals)


class TestCloudFeeds(SynchronousTestCase):
    def test_creation(self):
        """
        A new CloudFeeds plugin should have no products when created.
        """
        cf = cloudfeeds.CloudFeeds()
        self.assertEquals(len(cf.get_product_endpoints()), 0)

    def test_product_registration(self):
        """
        Registering a new product should create a new ATOM feed.
        """
        cf = cloudfeeds.CloudFeeds()
        cf.register_product(title='The hoohaw product.', href='hoohaw')
        self.assertEquals(len(cf.get_product_endpoints()), 1)

    def test_product_reregistration(self):
        """
        Re-registering a new product should do nothing.
        """
        cf = cloudfeeds.CloudFeeds()
        cf.register_product(title='The hoohaw product', href='hoohaw')
        cf.register_product(title='The OTHER hoohaw product', href='hoohaw')
        self.assertEquals(len(cf.get_product_endpoints()), 1)
        p = cf.get_product_by_href('hoohaw')
        self.assertEquals(p.title, 'The hoohaw product')

    def test_get_products(self):
        """
        Requesting a list of product endpoints should return a title and an href
        for each endpoint.
        """
        cf = cloudfeeds.CloudFeeds()
        cf.register_product(title='The hoohaw product', href='hoohaw')
        cf.register_product(title='The goober product', href='goober')
        products = cf.get_product_endpoints()
        self.assertEquals('hoohaw' in products, True)
        self.assertEquals(products['hoohaw'].title, 'The hoohaw product')
        self.assertEquals(products['goober'].title, 'The goober product')
        self.assertEquals(products['hoohaw'].href, 'hoohaw')
        self.assertEquals(products['goober'].href, 'goober')


class TestCloudFeedsProduct(SynchronousTestCase):
    def test_creation(self):
        """
        A new product queue should be empty.
        """
        cfp = cloudfeeds.CloudFeedsProduct(title='title', href='href')
        self.assertEquals(len(cfp.events), 0)

    def test_post(self):
        """
        Posting a new event to a queue should tack said event onto the end
        of said queue.
        """
        cfp = cloudfeeds.CloudFeedsProduct(title='title', href='href')
        cfp.post("TROLOLOLOLOL!!!")
        cfp.post("This is a totally fake event-like thing.")
        self.assertEquals(
            cfp.events,
            ["TROLOLOLOLOL!!!", "This is a totally fake event-like thing."]
        )


class TestSerialization(SynchronousTestCase):
    def test_json_description(self):
        """
        When listing product endpoints, we expect our JSON to look a certain
        way.  The easiest way to do that is to acquire the corresponding
        dict, then pass it through json.dump with your preferred formatting
        settings.
        """
        cfp = cloudfeeds.CloudFeedsProduct(title='title', href='href')
        d = cloudfeeds.render_product_dict(cfp)
        productDescription = MatchesDict({
            "title": Equals("title"),
            "collection": MatchesDict({
                "href": Equals("href"),
                "title": Equals("title"),
            }),
        })
        self.assertEquals(productDescription.match(d), None)

    def test_json_product_list(self):
        """
        When listing product endpoints, the resulting JSON should contain a
        service object, and a workspace object, and within that, an array of
        product descriptors.
        """
        cf = cloudfeeds.CloudFeeds()
        cf.register_product(title="The hoohaw product", href="hoohaw")
        cf.register_product(title="The goober product", href="goober")
        listing = MatchesDict({
            "service": MatchesDict({
                "workspace": MatchesSetwise({
                    MatchesDict({
                        "href": Equals("hoohaw"),
                        "title": Equals("The hoohaw product"),
                    }),
                    MatchesDict({
                        "href": Equals("goober"),
                        "title": Equals("The goober product"),
                    }),
                }),
            })
        })
        self.assertEquals(
            listing.match(cloudfeeds.render_product_endpoints_dict(
                cf.get_product_endpoints()
            )),
            None
        )
