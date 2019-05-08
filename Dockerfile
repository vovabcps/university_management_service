FROM gcr.io/google_appengine/python

RUN virtualenv /env -p python3.4
ENV PATH /env/bin:$PATH

ADD requirements.txt /app/requirements.txt
RUN /env/bin/pip install -r /app/requirements.txt
ADD . /app

CMD gunicorn -b :$PORT mysite.wsgi
