from flask import Flask, render_template, request
import pandas as pd
import pickle

app = Flask(__name__)
df = pd.read_csv("Cleaned_data.csv")
pipe = pickle.load(open("RidgeModel.pkl", "rb"))

@app.route('/')
def index():
    location = sorted(df['location'].unique())
    return render_template("index.html", location=location)

@app.route('/predict', methods=["POST"])
def predict():
    location = request.form.get("location")
    bath = request.form.get("bath")
    bhk = request.form.get("bhk")
    sqft = request.form.get("sqft")
    
    print(f"Location: {location}, BHK: {bhk}, Bath: {bath}, Square Feet: {sqft}")
    
    input = pd.DataFrame([[location, sqft, bath, bhk]], columns=['location', 'total_sqft', 'bath', 'bhk'])
    prediction = pipe.predict(input)[0] * 1e5

    # If the prediction is negative, return an error message
    if prediction < 0:
        return "Invalid price estimation. Please check your input values."
    
    # Format the prediction to make it more user-friendly
    formatted_prediction = format_prediction(prediction)
    
    return formatted_prediction


def format_prediction(prediction):
    """
    Function to format the prediction as lakhs, crores or with commas.
    """
    if prediction >= 1e7:  # More than 1 crore
        return format_in_crores(prediction)
    else:  # Less than 1 crore, use lakhs or full numbers with commas
        return format_in_lakhs(prediction)

def format_in_crores(prediction):
    """
    Format prediction for values in crores.
    """
    crores = prediction / 1e7
    crores_str = "{:,.2f}".format(crores)
    return f"₹{crores_str} cr"

def format_in_lakhs(prediction):
    """
    Format prediction for values in lakhs or regular numbers.
    """
    lakhs = prediction / 1e5
    lakhs_str = "{:,.0f}".format(lakhs)
    
    # If it's a smaller number, format it normally with commas
    if lakhs >= 1:
        return f"₹{lakhs_str} Lakh"
    else:
        # For cases where lakhs is less than 1 (less than ₹1 Lakh)
        return f"₹{int(prediction):,}"  # This will display the number in proper commas

if __name__ == "__main__":
    app.run(debug=True, port=5000)