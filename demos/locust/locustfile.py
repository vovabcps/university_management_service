from locust import HttpLocust, TaskSet
import json


USER_CREDENTIALS = [('fc'+str(i), 'blabla'+str(i)) for i in range(10, 610)]


def index(l):
    l.client.get("/student/home")


class UserBehavior(TaskSet):
    tasks = {index: 2}

    def on_start(self):
        user, passw = USER_CREDENTIALS.pop()
        payload = {"username": user, "password": passw}
        headers = {'content-type': 'application/json'}
        self.client.post("/",  data=json.dumps(payload), headers=headers, catch_response=True)


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 5000
    max_wait = 9000
