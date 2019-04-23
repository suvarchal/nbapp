from flask import Flask, redirect, url_for, request, session, escape,  render_template
import docker 
from time import sleep 
import time
import secrets
import tempfile
import string
import shutil
import json
import requests
import os 
from flask_sessions import Session
from redis_session.flask_session import setup_session


app = Flask(__name__)


app.config['SESSION_REDIS']='redis://redis:6379'

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or os.urandom(24)

app.config['SESSION_COOKIE_NAME'] = 'simplejhub'
app.config['PERMANENT_SESSION_LIFETIME'] = 1800

app.config.from_object(__name__)

#Session(app) # for flask sessions
setup_session(app) # redis ression

JUPYTER_CONTAINER= os.getenv("JUPYTER_CONTAINER","jupyter/base-notebook")
CULL_IDLE_TIMEOUT= os.getenv("CULL_IDLE_TIMEOUT",86400) # time out running notebook containers on inactivity
RAMADDA_BASE_URL = os.getenv("RAMADDA_BASE_URL".strip('/'),"https://weather.rsmas.miami.edu/repository") #can be auto based on request header
NOTEBOOK_HOST = os.getenv("NOTEBOOK_HOST".strip('/'),"localhost")



client=docker.from_env()

@app.route('/status',methods=['GET'])
def status(id):
    client.get('id')
    


#@app.route('/',methods=['GET','POST'])  
#def index():
#    if request.method == 'POST':
#        session['simplejhub-username'] = request.form['username']
#        return redirect(url_for('index'))
#
#    if 'simplejhub-username' in session:
#        return f"user name is {session['simplejhub-username']}" 
#    else:
#        return '''
#        <form method="post">
#            <p><input type=text name=username>
#            <p><input type=submit value=Login>
#        </form>
#    '''



@app.route('/logout')
def logout():
    "on logout stop container by name"
    try:
        username = session['simplejhub-username'] 
        user_container =client.containers.get(username)
        user_container.stop()
        session.clear()
    except:  
        session.clear()
    return 'logged out' 


def set_session():
    session.clear()
    username = 'user_'+''.join(secrets.choice(string.ascii_lowercase + string.ascii_lowercase) for _ in range(5))
    session['simplejhub-username'] = username
    tempdir = tempfile.mkdtemp(prefix=f'{username}_')
    session['simplejhub-path'] = tempdir
    return username, tempdir


@app.route('/notebook')
def jupyter_start():

    entryid = request.args.get('entryid','')

    #print(session.keys())
    
    if entryid:

        if 'simplejhub-username' in session:
            print('using existing session')
            username = session['simplejhub-username']
            tempdir  = session['simplejhub-path']
            redirect_path = f"http://{NOTEBOOK_HOST}/{username}/"
            try: 
                client.containers.get(username)
            except:
                username,tempdir = set_session()
                print("Created a new session for you ... ",username)
                redirect_path = create_container(username,tempdir)
                sleep(3) #creating container delay
                       
        else:
            username, tempdir = set_session()
            print("Created a new session for you ... ",username)
            redirect_path = create_container(username,tempdir)

            timeout =15
            sleep(3) # create container delay
        print("starting download")

        downloadinfo = "Downloading your notebook ..."
        r = requests.get(f"{RAMADDA_BASE_URL}/entry/show?entryid={entryid}&output=json")
        r_json = json.loads(r.content)[0]
        filename = r_json['filename']
        if filename.endswith('ipynb'): #instead use nbformat to check if file is a notebook, but this is faster.
            download_url = f"{RAMADDA_BASE_URL}/entry/get/{filename}?entryid={entryid}" 
            download_path = os.path.join(tempdir,filename) 
            save_file(download_url,download_path)
        else:
            return "Not a valid Jupyter Notebook?"
         
        #time.sleep(15)
        redirect_path=redirect_path+f"notebooks/{filename}"     
        
        #print('*************************REMOTREEEEE*****************************************')
        #print(request.remote_addr)
        #print(request.remote_addr)

        if NOTEBOOK_HOST != request.remote_addr:
            #print('******************************************************************')
            redirect_path=redirect_path.replace(NOTEBOOK_HOST,request.remote_addr)
            print(redirect_path)
        
        #print('----------------------')
        print(redirect_path) #for debugging
        return redirect(redirect_path, code=302)
        #return render_template('loading.html',redirect_path=redirect_path,timeout=10)# timeout)   
   # return(""" <label for="url">Enter an URL of Jupyter Notebook</label>
   #         <form method="post" enctype="application/x-www-form-urlencoded">
   #         <p><input type=url name=nburl placeholder="Jupyter Notebook URL">
   #         <p><input type=submit value=Live>
   #         </form>""")
    return "Nothing Yet!"

def create_container(username,volume,**kwargs):
    
    
    labels= {"traefik.frontend.rule":f"Host:{NOTEBOOK_HOST};PathPrefix:/{username}/"}
    volumes={volume: {'bind': '/home/jovyan/work', 'mode': 'rw'}}
    image = JUPYTER_CONTAINER # default is "jupyter/base-notebook"
    container = client.containers.run(image,
                   ["start-notebook.sh","--NotebookApp.base_url="+username+"/","--NotebookApp.token=''",
                   "--MappingKernelManager.cull_idle_timeout="+str(CULL_IDLE_TIMEOUT),
                   "--NotebookApp.shutdown_no_activity_timeout="+str(int(CULL_IDLE_TIMEOUT)+10),
                   "-y","work"],labels=labels,network="traefik_default",volumes=volumes,detach=True,remove=True,name=username ) 
#                   "--NotebookApp.allow_origin='*'","-y","work"],

    #print(container.logs())
    return f'http://{NOTEBOOK_HOST}/{username}/' #"http://localhost/"+user

def save_file(url,path):
    response = requests.get(url, stream=True)
    response.raw.decode_content = True
    print(path)
    #with open(path, 'wb') as f:
    #    for chunk in response.iter_content(1024*2):
    #        f.write(chunk)
    with open(path, 'wb') as f:
        response.raw.decode_content = True
        shutil.copyfileobj(response.raw, f)
    return True

##username scientist names
##js ping and redirect using window.location
## when a returning user returns return same notebook as previous session
## when a user shares then environment can be made fixed. 
## when user downloads a notebook, the environment is also given


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
