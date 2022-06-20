from unittest import TestCase

from app import app
from models import db, Cupcake

# Use test database and don't clutter tests with SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///cupcakes_test'
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

db.drop_all()
db.create_all()

CUPCAKE_DATA = {
    "flavor": "TestFlavor",
    "size": "TestSize",
    "rating": 5,
    "image": "http://test.com/cupcake.jpg"
}

CUPCAKE_DATA_2 = {
    "flavor": "TestFlavor2",
    "size": "TestSize2",
    "rating": 10,
    "image": "http://test.com/cupcake2.jpg"
}


class CupcakeViewsTestCase(TestCase):
    """Tests for views of API."""

    def setUp(self):
        """Make demo data."""

        Cupcake.query.delete()

        # "**" means "pass this dictionary as individual named params"
        cupcake = Cupcake(**CUPCAKE_DATA)
        db.session.add(cupcake)
        db.session.commit()

        self.cupcake = cupcake

    def tearDown(self):
        """Clean up fouled transactions."""

        db.session.rollback()

    def test_list_cupcakes(self):
        with app.test_client() as client:
            """ Test that we get a list of cupcakes in our database"""

            resp = client.get("/api/cupcakes")

            self.assertEqual(resp.status_code, 200)

            data = resp.json.copy()

            self.assertEqual(data, {
                "cupcakes": [
                    {
                        "id": self.cupcake.id,
                        "flavor": "TestFlavor",
                        "size": "TestSize",
                        "rating": 5,
                        "image": "http://test.com/cupcake.jpg"
                    }
                ]
            })

    def test_get_cupcake(self):
        with app.test_client() as client:
            """ Test that we get specific cupcake in our database"""

            url = f"/api/cupcakes/{self.cupcake.id}"
            resp = client.get(url)

            self.assertEqual(resp.status_code, 200)
            data = resp.json
            self.assertEqual(data, {
                "cupcake": {
                    "id": self.cupcake.id,
                    "flavor": "TestFlavor",
                    "size": "TestSize",
                    "rating": 5,
                    "image": "http://test.com/cupcake.jpg"
                }
            })

    def test_create_cupcake(self):
        with app.test_client() as client:
            """ Test that we can add a cupcake into our database"""

            url = "/api/cupcakes"
            resp = client.post(url, json=CUPCAKE_DATA_2)

            self.assertEqual(resp.status_code, 201)

            data = resp.json.copy()

            # don't know what ID we'll get, make sure it's an int & normalize
            self.assertIsInstance(data['cupcake']['id'], int)
            del data['cupcake']['id']

            self.assertEqual(data, {
                "cupcake": {
                    "flavor": "TestFlavor2",
                    "size": "TestSize2",
                    "rating": 10,
                    "image": "http://test.com/cupcake2.jpg"
                }
            })

            self.assertEqual(Cupcake.query.count(), 2)

    def test_update_cupcake(self):
        with app.test_client() as client:
            """ Test that we get update a cupcake's info in our database"""

            new_cupcake_resp = client.post(
                "/api/cupcakes", json=CUPCAKE_DATA_2)
            new_cupcake_data = new_cupcake_resp.json

            id = new_cupcake_data['cupcake']['id']

            url = f"/api/cupcakes/{id}"
            updated_resp = client.patch(
                url, json={"size": "test-changed-size"})

            updated_data = updated_resp.json

            self.assertEqual(updated_resp.status_code, 200)

            self.assertEqual(updated_data, {
                "cupcake": {
                    "id": new_cupcake_data['cupcake']['id'],
                    "flavor": "TestFlavor2",
                    "size": "test-changed-size",
                    "rating": 10,
                    "image": "http://test.com/cupcake2.jpg"
                }
            })

            self.assertEqual(Cupcake.query.count(), 2)

    def test_delete_cupcake(self):
        with app.test_client() as client:
            """ Test that we get delete a cupcake in our database"""

            new_cupcake_resp = client.post(
                "/api/cupcakes", json=CUPCAKE_DATA_2)
            new_cupcake_data = new_cupcake_resp.json

            url = f"/api/cupcakes/{new_cupcake_data['cupcake']['id']}"
            deleted_resp = client.delete(url)
            deleted_data = deleted_resp.json

            self.assertEqual(deleted_resp.status_code, 200)

            self.assertEqual(deleted_data, {
                "deleted": [new_cupcake_data['cupcake']['id']]
            })

            self.assertEqual(Cupcake.query.count(), 1)
