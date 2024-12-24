import google.generativeai as genai
import streamlit as st
from PIL import Image, ImageDraw, ImageFont


# Configure the API key for Gemini AI
def configure_api():

  genai.configure(api_key=gemini_api_key)

# Initialize the UI elements
def create_ui():
  emoji = "🎉"
  st.markdown(
    f"""
        <div style="display: flex; align-items: center;">
            <span style="font-size: 30px; margin-right: 10px;">{emoji}</span>
            <h1 style="margin: 0; color: #BB86FC;">Greetings Galore</h1>
        </div>
    """,
    unsafe_allow_html=True
  )
  st.subheader(":blue[Personalized greetings for every occasion]", divider="rainbow")

# Define options for occasions, languages, and tones
def get_options():
    occasions = [
        "New Year's Day", "Valentine's Day", "Holi", "Easter", "Mother's Day", 
        "Father's Day", "Independence Day", "Christmas", "Dussehra", "Diwali", 
        "Ramzan", "Onam", "Vishu", "Birthday"
    ]
    relationships = ["Professional","Friend","Family"]
    family_relationships = ["Parent","Sibling","Spouse/Partner","Child","Grandparent","Other Relative"]
    friend_relationships = ["Close Friend", "Acquaintance"]
    professional_relationships = ["Manager","Coworker","Client","Mentor","Senior Leader"]
    tones = ["Professional", "Heartfelt", "Fun", "Traditional", "Poetic"]

    return occasions, tones, relationships, family_relationships, friend_relationships, professional_relationships

# Get the selected options from the user
def get_user_inputs(occasions, tones, relationships, family_relationships, friend_relationships, professional_relationships):
  col1, col2 = st.columns(2)

  with col1:
    selected_occasion = st.selectbox("Select occasion", sorted(occasions))

  with col2:
    tone = st.selectbox("Select tone", sorted(tones))

  col3, col4 = st.columns(2)

  with col3:
    selected_relationship = st.selectbox("Select relationship", relationships)

  with col4:
    if selected_relationship == "Family":
        specific_relationship = st.selectbox("Select family member", family_relationships)
    elif selected_relationship == "Friend":
        specific_relationship = st.selectbox("Select friend type", friend_relationships)
    else:  # Professional
        specific_relationship = st.selectbox("Select professional role", professional_relationships)

  text_color = st.color_picker("Select text color", "#000000")
  return selected_occasion,  selected_relationship, specific_relationship, tone, text_color


# Set up the Gemini AI model
def setup_gemini_model():
  generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
  }

  model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
  )
  return model.start_chat(history=[])

def get_font_for_language(size):
    font_map = "/usr/share/fonts/truetype/noto/DejavuSans.ttf"  # Default font path
    return ImageFont.truetype(font_map, size)

# Generate the greeting message
def generate_greeting(chat_session, tone, occasion, relationship, specific_relationship):
  prompt = f"Give me a short greeting message in a {tone} tone for {specific_relationship} in the context of {relationship} for {occasion}"
  response = chat_session.send_message(prompt)
  return response.text

# Generate the greeting message
def generate_image(greeting_draft, font, custom_image, text_color ):
  image = custom_image
  outfile = "./output.png"
  draw = ImageDraw.Draw(image)

  text_bbox = draw.textbbox((0, 0), greeting_draft, font=font)
  text_x = (image.width - (text_bbox[2] - text_bbox[0])) / 2
  text_y = (image.height - (text_bbox[3] - text_bbox[1])) / 2

  draw.multiline_text((text_x, text_y), greeting_draft, font=font, fill=text_color, align="center")

  credit_text = "@Greetings Galore"
  credit_font = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf", 10)
  credit_bbox = draw.textbbox((0, 0), credit_text, font=credit_font)
  credit_x = (image.width - (credit_bbox[2] - credit_bbox[0])) / 2
  credit_y = image.height - 20
  draw.text((credit_x, credit_y), credit_text, font=credit_font, fill=(239, 210, 171))

  image.save(outfile, "PNG")
  return outfile

def main():
  configure_api()
  create_ui()
  occasions, tones, relationships, family_relationships, friend_relationships, professional_relationships = get_options()

  occasion, relationship, specific_relationship, tone, text_color = get_user_inputs(
        occasions, tones, relationships, family_relationships, friend_relationships, professional_relationships
  )
  font = get_font_for_language(24)

  chat_session = setup_gemini_model()

  uploaded_image = st.file_uploader("Upload background image", type=["png","jpg","jpeg"])
  if uploaded_image:
    custom_image = Image.open(uploaded_image)
    st.image(custom_image, caption="Uploaded Image", use_column_width=True)
  else:
    st.warning("Please upload an image to proceed.")

  if 'greeting_draft' not in st.session_state:
    st.session_state.greeting_draft = ""

  if st.button("Generate Message"):
    st.session_state.greeting_draft = generate_greeting(chat_session, tone, occasion, relationship, specific_relationship)

  greeting_draft = st.text_area("Modify the draft as needed:", st.session_state.greeting_draft)

  if st.button("Confirm"):
    st.write("Message preview:")
    st.markdown(f"<p style='color: {text_color};'>{greeting_draft}</p>", unsafe_allow_html=True)

  if st.button("Generate Image") and uploaded_image:
    outfile = generate_image(greeting_draft, font, custom_image, text_color)
    st.image(outfile)

    with open(outfile, "rb") as file:
      btn = st.download_button(
        label="Download Image",
        data=file,
        file_name="greeting_image.png",
        mime="image/png")

if __name__ == "__main__":
    main()
