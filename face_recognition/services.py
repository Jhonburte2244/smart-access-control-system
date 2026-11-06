
import base64
from pathlib import Path

import cv2
import numpy as np


# ============================================================
# MODEL PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

YUNET_MODEL = BASE_DIR / "models" / "face_detection_yunet.onnx"
SFACE_MODEL = BASE_DIR / "models" / "face_recognition_sface.onnx"


# ============================================================
# FACE RECOGNITION ENGINE
# ============================================================

class FaceRecognitionService:

    def __init__(self):

        if not YUNET_MODEL.exists():
            raise FileNotFoundError(
                f"YuNet model not found: {YUNET_MODEL}"
            )

        if not SFACE_MODEL.exists():
            raise FileNotFoundError(
                f"SFace model not found: {SFACE_MODEL}"
            )

        # ----------------------------------------------------
        # Face detector
        # ----------------------------------------------------

        self.detector = cv2.FaceDetectorYN.create(
            str(YUNET_MODEL),
            "",
            (320, 320),
            0.9,
            0.3,
            5000,
        )

        # ----------------------------------------------------
        # Face recognizer
        # ----------------------------------------------------

        self.recognizer = cv2.FaceRecognizerSF.create(
            str(SFACE_MODEL),
            "",
        )

    # ========================================================
    # LOAD IMAGE
    # ========================================================

    @staticmethod
    def load_image(image_path):

        image = cv2.imread(str(image_path))

        if image is None:
            raise ValueError(
                f"Unable to read image: {image_path}"
            )

        return image

    # ========================================================
    # DETECT FACE
    # ========================================================

    def detect_face(self, image):

        height, width = image.shape[:2]

        self.detector.setInputSize(
            (width, height)
        )

        _, faces = self.detector.detect(image)

        if faces is None or len(faces) == 0:
            raise ValueError(
                "No face detected in the image."
            )

        if len(faces) > 1:
            raise ValueError(
                "Multiple faces detected. "
                "Please use an image containing only one person."
            )

        return faces[0]

    # ========================================================
    # EXTRACT FACE FEATURE
    # ========================================================

    def extract_feature(self, image):

        face = self.detect_face(image)

        aligned_face = self.recognizer.alignCrop(
            image,
            face,
        )

        feature = self.recognizer.feature(
            aligned_face
        )

        if feature is None:
            raise ValueError(
                "Unable to extract face feature."
            )

        return feature

    # ========================================================
    # VALIDATE FACE IMAGE
    # ========================================================

    def validate_image(self, image_path):

        image = self.load_image(image_path)

        face = self.detect_face(image)

        feature = self.extract_feature(image)

        return {
            "face": face,
            "feature": feature,
            "image": image,
        }

    # ========================================================
    # FEATURE → DATABASE STRING
    # ========================================================

    @staticmethod
    def feature_to_string(feature):

        feature_bytes = feature.astype(
            np.float32
        ).tobytes()

        encoded = base64.b64encode(
            feature_bytes
        ).decode("utf-8")

        return encoded

    # ========================================================
    # DATABASE STRING → FEATURE
    # ========================================================

    @staticmethod
    def string_to_feature(template_data):

        if not template_data:
            raise ValueError(
                "Face template is empty."
            )

        try:

            feature_bytes = base64.b64decode(
                template_data
            )

            feature = np.frombuffer(
                feature_bytes,
                dtype=np.float32,
            )

            if feature.size == 0:
                raise ValueError(
                    "Face template contains no feature data."
                )

            return feature.reshape(
                1,
                -1,
            )

        except Exception as error:

            raise ValueError(
                f"Invalid face template data: {error}"
            )

    # ========================================================
    # IMAGE → TEMPLATE
    # ========================================================

    def create_template(self, image_path):

        image = self.load_image(
            image_path
        )

        feature = self.extract_feature(
            image
        )

        return self.feature_to_string(
            feature
        )

    # ========================================================
    # COMPARE TWO FEATURES
    # ========================================================

    def compare_features(
        self,
        feature1,
        feature2,
    ):

        score = self.recognizer.match(
            feature1,
            feature2,
            cv2.FaceRecognizerSF_FR_COSINE,
        )

        return float(score)

    # ========================================================
    # COMPARE IMAGE AGAINST TEMPLATE
    # ========================================================

    def compare_image_to_template(
        self,
        image_path,
        template_data,
    ):

        image = self.load_image(
            image_path
        )

        current_feature = self.extract_feature(
            image
        )

        stored_feature = self.string_to_feature(
            template_data
        )

        score = self.compare_features(
            current_feature,
            stored_feature,
        )

        return score

    # ========================================================
    # RECOGNIZE IMAGE
    # ========================================================

    def recognize_image(
        self,
        image_path,
        templates,
    ):
        """
        Recognize a face from an image against stored
        face templates.

        SFace cosine similarity:
            0.0 - 1.0

        Database confidence threshold:
            0.0 - 100.0

        The similarity is converted to percentage
        before comparing with the database threshold.
        """

        image = self.load_image(
            image_path
        )

        # ----------------------------------------------------
        # Extract feature from submitted image
        # ----------------------------------------------------

        current_feature = self.extract_feature(
            image
        )

        best_match = None
        best_score = -1.0

        # ----------------------------------------------------
        # Compare against stored templates
        # ----------------------------------------------------

        for template in templates:

            if not template.template_data:
                continue

            try:

                stored_feature = (
                    self.string_to_feature(
                        template.template_data
                    )
                )

                raw_score = (
                    self.compare_features(
                        current_feature,
                        stored_feature,
                    )
                )

                score_percent = raw_score * 100.0

                if score_percent > best_score:

                    best_score = score_percent
                    best_match = template

            except Exception:

                # Ignore invalid template
                # and continue checking others.
                continue

        # ----------------------------------------------------
        # No valid templates
        # ----------------------------------------------------

        if best_match is None:

            return {
                "recognized": False,
                "employee": None,
                "template": None,
                "score": 0.0,
                "threshold": None,
            }

        # ----------------------------------------------------
        # Threshold
        # ----------------------------------------------------

        threshold = float(
            best_match.confidence_threshold or 80.0
        )

        # ----------------------------------------------------
        # Recognition decision
        # ----------------------------------------------------

        recognized = (
            best_score >= threshold
        )

        return {
            "recognized": recognized,
            "employee": (
                best_match.employee
                if recognized
                else None
            ),
            "template": best_match,
            "score": best_score,
            "threshold": threshold,
        }
