from PIL import Image
from io import BytesIO
import base64
import logging
from datetime import datetime

logger = logging.getLogger()


def generate_textual_summary(lida, textgen_config, df):
    # lida, textgen_config = st.session_state["lida"], st.session_state["textgen_config"]
    
    summary = lida.summarize(
        df, summary_method="default", textgen_config=textgen_config
    )
    # return response.choices[0].text.strip()
    return summary

# Function to convert base64 to Image object
def _base64_to_image(base64_string, image_path):
    byte_data = base64.b64decode(base64_string)
    with open(image_path, 'wb') as file:
        file.write(byte_data)
    img = Image.open(BytesIO(byte_data))
    # img= cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB)
    return img

def get_explaination(lida, textgen_config, visualization, library="matplotlib"):
    # lida, textgen_config = st.session_state["lida"], st.session_state["textgen_config"]
    visuals_explain = lida.explain(code=visualization.code, textgen_config=textgen_config, 
                                       library=library)
    return visuals_explain

# Function to edit visualization based on natural language instructions
def vis_edit(lida, textgen_config, visualization, summary, instructions, library="matplotlib"):
#    lida, textgen_config = st.session_state["lida"], st.session_state["textgen_config"]
   edited_charts = lida.edit(code=visualization.code, summary=summary, instructions=instructions, library=library, textgen_config=textgen_config)
   image_path = f'data/graphs/visualization_{datetime.now():%Y-%m-%d_%H-%M-%S}.png'
   imgs = []
   imgs_paths = []
   visuals = []
   if edited_charts:
       visualization = edited_charts[0]
       image_base64 = visualization.raster
       logger.info(f"Error {visualization.error}")
       logger.info(f"library {visualization.library}")
       logger.info("spec {visualization.spec}")
       logger.info("status {visualization.status}")
       logger.info("Code")
       print("'''"*20)
       logger.debug(visualization.code)
       print("'''"*20)



       img = _base64_to_image(image_base64, image_path)
       imgs.append(img)
       imgs_paths.append(image_path)
       visuals.append(visualization)
       return imgs, imgs_paths, visuals 
   else:
       return None      

def get_goals(lida, textgen_config, summary, no_of_goal =2):
    # lida, textgen_config = st.session_state["lida"], st.session_state["textgen_config"]
    goals = lida.goals(summary, n=no_of_goal, textgen_config=textgen_config)
    return goals

# def get_visuals(lida, textgen_config, summary, kpi_query,  library="matplotlib"):
#     # lida, textgen_config = st.session_state["lida"], st.session_state["textgen_config"]
#     visualizations = lida.visualize(
#     summary=summary,
#     goal=kpi_query,
#     textgen_config=textgen_config,
#     library=library,)
#     imgs = []
#     imgs_paths = []
#     visuals = []
#     for visualization in visualizations:
#         image_path = f'data/graphs/visualization_{datetime.now():%Y-%m-%d_%H-%M-%S}.png'
#         # print(dir(visualization))
#         image_base64 = visualization.raster
#         logger.info(f"Error: {visualization.error}")
#         logger.info(f"library: {visualization.library}")
#         logger.info(f"spec: {visualization.spec}")
#         logger.info(f"status: {visualization.status}")
#         logger.info("Code:")
#         logger.debug(f"Code: \n{visualization.code}")
#         img = _base64_to_image(image_base64, image_path)
#         imgs.append(img)
#         imgs_paths.append(image_path)
#         visuals.append(visualization)
#     return imgs, imgs_paths, visuals

def get_visuals(lida, textgen_config, summary, kpi_query, library="matplotlib"):
    visualizations = lida.visualize(summary=summary,goal=kpi_query,textgen_config=textgen_config,library=library,return_error=True)
    imgs = []
    imgs_paths = []
    visuals = []
 
    for visualization in visualizations:
        image_path = f'data/graphs/visualization_{datetime.now():%Y-%m-%d_%H-%M-%S}.png'
        if visualization.status:
            image_base64 = visualization.raster
            logger.info(f"Error: {visualization.error}")
            logger.info(f"library: {visualization.library}")
            logger.info(f"spec: {visualization.spec}")
            logger.info(f"status: {visualization.status}")
            logger.info("Code:")
            logger.debug(f"Code: \n{visualization.code}")
            img = _base64_to_image(image_base64, image_path)
            imgs.append(img)
            imgs_paths.append(image_path)
            visuals.append(visualization)
        else:
            visualizations = lida.repair(code=visualization.code, summary=summary, goal=kpi_query, library=library,feedback=visualization.error )
            for visualization in visualizations:
                image_base64 = visualization.raster
                logger.info(f"Error: {visualization.error}")
                logger.info(f"library: {visualization.library}")
                logger.info(f"spec: {visualization.spec}")
                logger.info(f"status: {visualization.status}")
                logger.info("Code:")
                logger.debug(f"Code: \n{visualization.code}")
                img = _base64_to_image(image_base64, image_path)
                imgs.append(img)
                imgs_paths.append(image_path)
                visuals.append(visualization)
    
    return imgs, imgs_paths, visuals

if __name__ == "__main__":
    # Initialize LIDA manager with text generation configuration
    from lida import Manager, TextGenerationConfig, llm
    import deereai as deereai
    import pandas as pd
 
    # intialise data of lists.
    data = {'Name':['Tom', 'nick', 'krish', 'jack'],
            'Age':[20, 21, 19, 18]}
    
    # Create DataFrame
    df = pd.DataFrame(data)
    bearer_token = deereai.get_deereai_token()
    api_base = "https://mlops-api.deere.com/language-model-deployments/1635/invocations"
    text_gen = llm(provider="deereai", bearer_token=bearer_token, api_base=api_base)
    textgen_config = TextGenerationConfig(
        n=1, temperature=0.5, model="gpt-3.5-turbo-0301", use_cache=False
    )
    lida = Manager(text_gen=text_gen)
    textual_summary = generate_textual_summary(lida, textgen_config, df)

    visuals = get_visuals(lida, textual_summary,"histogram of name by age " , textgen_config)

