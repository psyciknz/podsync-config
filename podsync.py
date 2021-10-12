from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, RadioField, SubmitField,FileField
from wtforms.validators import DataRequired,URL,Regexp
import toml
import io

app = Flask(__name__)

# Flask-WTF requires an enryption key - the string can be anything
app.config['SECRET_KEY'] = 'C2HWGVoMGfNTBsrYQg8EcMrdTimkZfAb'

# Flask-Bootstrap requires this line
Bootstrap(app)

# with Flask-WTF, each web form is represented by a class
# "NameForm" can change; "(FlaskForm)" cannot
# see the route for "/" and "index.html" to see how this is used
class ChannelForm(FlaskForm):
    #name [feeds.colinfurze]
    #url = "https://www.youtube.com/user/colinfurze" # URL address of a channel, group, user, or playlist.
    #page_size = 10 # The number of episodes to query each update (keep in mind, that this might drain API token)
    #update_period = "20h" # How often query for updates, examples: "60m", "4h", "2h45m"
    #quality = "high" # or "low"
    #format = "video" # or "audio"
    #clean = { keep_last = 10 }
    
    name = StringField('Name of the Channel' , validators=[DataRequired()])
    url = StringField("URL address of a channel, group, user, or playlist.",validators=[DataRequired(),URL()])
    page_size = IntegerField("The number of episodes to query each update (keep in mind, that this might drain API token)", validators=[DataRequired()])
    update_period = StringField("How often query for updates, examples: ""60m"", ""4h"", ""2h45m""", validators=[DataRequired(),Regexp("\d+[mh]")])
    quality = RadioField("Quality",choices=[("high","high"),("low","low")])
    format = RadioField("Format",choices=[("video","video"),("audio","audio")])
    clean = IntegerField("How many to keep")
    file = FileField('Podsync Config')

    submit = SubmitField('Submit')

# all Flask routes below
class OpenForm(FlaskForm):
    file = FileField('Podsync Config')
    submit = SubmitField('Submit')

class PickleableTomlDecoder(toml.TomlDecoder):
     def get_empty_inline_table(self):
         return self.get_empty_inline_table

@app.route('/', methods=['GET', 'POST'])
def index():
    # you must tell the variable 'form' what you named the class, above
    # 'form' is the variable name used in this template: index.html
    form = ChannelForm()
    message = ""
    if form.validate_on_submit():
        name = form.name.data 
        url = form.url.data
        page_size = form.page_size.data
        update_period = form.update_period.data
        quality = form.quality.data
        format = form.format.data
        clean = form.clean.data
        filename = form.file.data.filename
        print(filename)
        # load existing toml from file.
        file_toml = ""
        with open(filename,'r') as f:
            file_toml = toml.load(f)

        print(file_toml['feeds'])
        if not  name in file_toml['feeds']:
            new_entry = dict()
            new_entry['url']=url
            new_entry['page_size']=page_size
            new_entry['update_period']=update_period
            new_entry['quality']=quality
            new_entry['format']=format
            
            enc =  toml.encoder.TomlEncoder(preserve=True)
            
            cleantable = toml.TomlDecoder().get_empty_inline_table()
            #cleantable.append({'keep_last':10})
            cleantable['keep_last']=10

            new_entry['clean'] = cleantable
            #"{ keep_last = %d}" % clean
            #file_toml['feeds'].append('feeds.' + name)
            file_toml['feeds'][name] = new_entry
            with open(filename,'w') as f:
                toml.dump(file_toml,f,encoder=enc)
                #f.write(toml.dumps(file_toml,preserve=True))
            message = "Feed "" + name + "" written to podsync config "
        else:
            message = "Feed "" + name + "" already existed"
    else:
        print(form.errors)
    #    
    return render_template('index.html', form=form, message=message)

@app.route('/open', methods=['GET', 'POST'])
def openfile():
    # you must tell the variable 'form' what you named the class, above
    # 'form' is the variable name used in this template: index.html
    form = OpenForm()
    message = ""
    if form.validate_on_submit():
        filename = form.file.data.filename
        print(filename)
        with open(filename,'r') as f:
            new_toml_string = toml.load(f)
        
        print(new_toml_string)
        message = toml.dumps(new_toml_string)
        

    else:
        print(form.errors)
    #    
    return render_template('open.html', form=form, message=message)    

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


# keep this as is
if __name__ == '__main__':
    #with open('config.toml','r') as f:
    #    vlues = toml.load(f)

    #vlues['feeds']['newfeed'] = dict()
    #vlues['feeds']['newfeed']['url'] = "hello"
    #cleantable = {}
    #cleantable['keep_last']=10

    #vlues['feeds']['newfeed']['clean'] = cleantable

    app.run(debug=True)
