"""
Get started with our docs, https://docs.beam.cloud
"""
from beam import App, Runtime

app = App(
    "gdd_calculator",
    runtime=Runtime(
        cpu=1,
        memory="8Gi",
    )
)

# Triggers determine how your app is deployed
@app.rest_api()
def hello_world(**inputs):
    print("After deploying, you'll see these logs in the web dashboard 👀")
    return {"response": "hello world"}

if __name__ == "__main__":
    text = "Testing 123"
    hello_world(text=text)