import os


TEST_JWT_SECRET = "edunova-test-jwt-secret-for-automated-tests-only"

os.environ.setdefault(
    "EDUNOVA_JWT_SECRET",
    TEST_JWT_SECRET,
)
