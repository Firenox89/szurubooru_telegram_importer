FROM python:3

ADD *.py /
ADD requirements.txt /

run pip install -r requirements.txt

CMD [ "python", "./sir_gram_a_lot.py" ]
