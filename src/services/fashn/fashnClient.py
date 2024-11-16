import base64
import os
import logging
from time import sleep
import httpx

logger = logging.getLogger(__name__)

Fashn_BASE_URL = "https://api.fashn.ai/v1"
_TIMEOUT = 60


# Have to use jpg for the base64 encoding
# TODO: support other image format


class FashnClient:
    _instance = None
    _client = None

    def __init__(self):
        if FashnClient._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            api_key = os.getenv("FASHN_API_KEY")
            if not api_key:
                logger.error("Fashn API key not found in environment variables")
                raise ValueError("FASHN_API_KEY environment variable is not set")
            FashnClient._instance = self
            self._client = httpx.Client(
                base_url=Fashn_BASE_URL,
                headers={"Authorization": f"Bearer {api_key}"},
            )

    @classmethod
    def getInstance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _get_image_md5_content(self, image_path) -> tuple[str, bytes]:
        with open(image_path, "rb") as fp:
            content = fp.read()
            image_md5 = base64.b64encode(content).decode("utf-8")
            base64_string = "data:image/jpg;base64," + image_md5
        return base64_string

    # https://developer.Fashnni.ai/api/#section/Examples
    def _upload_image(self, model_image_path, cloth_image_path, clothing_type):
        encoded_image_model = self._get_image_md5_content(model_image_path)
        encoded_image_cloth = self._get_image_md5_content(cloth_image_path)

        response = self._client.post(
            "/run",
            json={
                "model_image": encoded_image_model,
                "garment_image": encoded_image_cloth,
                "category": clothing_type,  # TODO support other types 'tops' | 'bottoms' | 'one-pieces'
            },
        )
        body = response.json()
        task_id = body["id"]

        return task_id

    def _get_image(self, task_id):
        response = self._client.get(
            f"/status/{task_id}",
        )
        return response.json()

    def wear_it(self, model_image_path, cloth_image_path, clothing_type):
        task_id = self._upload_image(model_image_path, cloth_image_path, clothing_type)
        response = None

        # Get the image
        for i in range(50):
            response = self._get_image(task_id)
            if response["status"] == "completed" or response["error"] is not None:
                break
            else:
                print("sleeping")
                sleep(2)

        if response["error"] is not None:
            print(response["error"])
            return response["error"]

        # Print the output URL to download the enhanced image
        output_url = response["output"][0]
        return output_url


client = FashnClient.getInstance()
# result = client.wear_it("person.jpg", "blue_dress.jpg", "tops")
result = client.wear_it("person.jpg", "blue_dress.jpg", "one-pieces")
print(
    result
)  # {'name': 'PoseError', 'message': 'Failed to detect body pose in garment image.'}
