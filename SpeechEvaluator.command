cd -- "$(dirname "$0")"

pip3 install -r requirements.txt
python3 ./video/tf-pose-estimation/setup.py install
python3 speech_evaluator.py
