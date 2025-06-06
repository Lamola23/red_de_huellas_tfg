from locust import HttpUser, task, between

class UsuarioSimulado(HttpUser):
    wait_time = between(1, 3) 

    def on_start(self):
        self.client.post("/login/", data={
            "username": "monicaortega0023@gmail.com",
            "password": "@Monica1"
        })

    @task
    def inicio(self):
        self.client.get("/")  

    @task
    def animales(self):
        self.client.get("/animales/") 

    @task
    def detalle_animal(self):
        self.client.get("/animal/1/")


class MyUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def load_home(self):
        self.client.get("/")