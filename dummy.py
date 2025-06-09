workflow:
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

stages:
  - build
  - test
  - publish_int
  - deploy_int
  - publish_prod
  - deploy_prod

variables:
  INDEX_URL_PRD: https://$JF_USER:$JF_ACCESS_TOKEN_PRD@$JF_URL_PRD
  INDEX_URL_INT: https://$JF_USER:$JF_ACCESS_TOKEN_INT@$JF_URL_INT


build-wheel-and-sdist:
  stage: build
  image: python:3.12-alpine
  before_script:
    - apk add --no-cache git
  script:
    - pip install --upgrade pip setuptools wheel build
    # 2. Build source and wheel distributions
    - python3 -m build --sdist --wheel .

  artifacts:
    paths:
      - dist/*.whl
    expire_in: 1 week

.test_wheel_tox:
  stage: test
  image: python:3.12-alpine
  dependencies:
    - build-wheel-and-sdist
  before_script:
    # install tox itself
    - python -m pip install --upgrade pip tox
  script:
    - python -c "import app; print(app.__file__); print(app.__path__[0])"
    - unzip -l dist/*.whl | grep -E "app/__init__.py"
    # this will create its own env, install your wheel, run pytest+cov
    - WHEEL_FILE=$(ls dist/*.whl)
    - sed -i "s|{WHEEL_FILE}|$WHEEL_FILE|g" pyproject.toml
    - python -m pip install "$WHEEL_FILE"
    - rm -rf ./app
    - python -c "import app; print(app.__file__); print(app.__path__[0])"
    - tox -e wheel
    - mv coverage.xml "$CI_PROJECT_DIR/test-reports/" || true
    - mv htmlcov       "$CI_PROJECT_DIR/test-reports/" || true
    - mv .coverage     "$CI_PROJECT_DIR/test-reports/" || true

  artifacts:
    paths:
      - test-reports
    when: always
    expire_in: 1 week
    reports:
      junit: test-reports/report.xml
      coverage_report:
        coverage_format: cobertura
        path: test-reports/coverage.xml

test_wheel:
  stage: test
  image: python:3.12-alpine
  dependencies:
    - build-wheel-and-sdist
  variables:
    THIS_DIR: "$CI_PROJECT_DIR"
  before_script:
    - rm -rf test-env || true
    - python -m venv test-env
    - source test-env/bin/activate
    - pip install build pytest pytest-cov
  script:
    - python -c "import app; print(app.__file__); print(app.__path__[0])"

    - python -m pip install dist/*.whl
    - rm -rf ./app
    - python -c "import app; print(app.__file__); print(app.__path__[0])"
    - |
      python -m pytest -vv -s --import-mode=append ${@:-"$THIS_DIR/tests/"} \
          --cov "app" \
          --cov-report html \
          --cov-report term \
          --cov-report xml \
          --junit-xml "$THIS_DIR/test-reports/report.xml" \
          --cov-fail-under 60
    - mv coverage.xml "$CI_PROJECT_DIR/test-reports/" || true
    - mv htmlcov       "$CI_PROJECT_DIR/test-reports/" || true
    - mv .coverage     "$CI_PROJECT_DIR/test-reports/" || true

  artifacts:
    paths:
      - test-reports
    when: always
    expire_in: 1 week
    reports:
      junit: test-reports/report.xml
      coverage_report:
        coverage_format: cobertura
        path: test-reports/coverage.xml


publish_jfrog_int:
  stage: publish_int
  image: python:3.12-alpine
  needs:
    - job: test_wheel
    - job: build-wheel-and-sdist
      artifacts: true
  before_script:
    - pip install --upgrade pip setuptools wheel twine
  script:
    - echo "UPLOding..."
    #- twine upload --non-interactive --repository-url ${JF_URL_INT} dist/*.whl -u ${JF_USER} -p ${JF_ACCESS_TOKEN_INT}

deploy_jfrog_int:
  stage: deploy_int
  image: python:3.12-alpine
  dependencies:
    - publish_jfrog_int
  before_script:
    - apk add --no-cache git
    - pip install setuptools_scm
  script:
    - VERSION=$(python -m setuptools_scm)
    - echo $VERSION
    #- pip install --index-url $INDEX_URL_INT app==${VERSION}


publish_jfrog_prd:
  stage: publish_prod
  image: python:3.12-alpine
  needs:
    - job: test_wheel
    - job: build-wheel-and-sdist
      artifacts: true
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
    - if: $CI_COMMIT_TAG
  before_script:
    - pip install --upgrade pip setuptools wheel twine
  script:
    #- twine upload --non-interactive --repository-url ${JF_URL_PRD} dist/*.whl -u ${JF_USER} -p ${JF_ACCESS_TOKEN_PRD}
    - echo "UPLOADING..."

deploy_jfrog_prod:
  stage: deploy_prod
  image: python:3.12-alpine
  dependencies:
    - publish_jfrog_prd
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
    - if: $CI_COMMIT_TAG
  before_script:
    - apk add --no-cache git
  script:
    - echo "UPLOADING..."
