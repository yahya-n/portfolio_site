from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_mail import Mail, Message
from utils import load_data, save_data, load_analytics, save_analytics
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import re
from config import config

app = Flask(__name__)

# Load Configuration
# Determine environment: 'production' if DEPLOYMENT_MODE is 'true', else 'development'
deployment_mode = os.getenv('DEPLOYMENT_MODE', 'False').lower() in ['true', '1', 't']
config_name = 'production' if deployment_mode else 'development'
app.config.from_object(config[config_name])

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

mail = Mail(app)

# Middleware for Analytics
@app.before_request
def track_visits():
    if request.path.startswith('/static') or request.path.startswith('/admin') or request.path.startswith('/api'):
        return
    
    analytics = load_analytics()
    
    # Track Daily Visits
    today = datetime.now().strftime('%Y-%m-%d')
    analytics['daily_visits'][today] = analytics['daily_visits'].get(today, 0) + 1
    
    # Track Page Views
    path = request.path
    analytics['page_views'][path] = analytics['page_views'].get(path, 0) + 1
    
    save_analytics(analytics)

@app.route('/api/track_section', methods=['POST'])
def track_section():
    data = request.json
    section = data.get('section')
    if section:
        analytics = load_analytics()
        analytics['section_views'][section] = analytics['section_views'].get(section, 0) + 1
        save_analytics(analytics)
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error'}), 400

@app.route('/debug/email')
def debug_email():
    # Only allow debug routes in development or if specifically enabled? 
    # For now, let's just use the config, but be careful in prod.
    if not app.config.get('DEBUG') and not app.config.get('TESTING'):
         return "Debug routes disabled in production", 403

    try:
        username = app.config.get('MAIL_USERNAME')
        password = app.config.get('MAIL_PASSWORD')
        
        if not username or not password:
            return f"Error: Credentials missing. Username: {username}, Password set: {bool(password)}"

        msg = Message("Test Email from Portfolio",
                      sender=username,
                      recipients=[username])
        msg.body = "This is a test email to verify your SMTP configuration."
        mail.send(msg)
        return f"Email sent successfully to {username}!"
    except Exception as e:
        import traceback
        return f"<h1>Email Sending Failed</h1><pre>{traceback.format_exc()}</pre>"

@app.route('/')
def index():
    data = load_data()
    return render_template('index.html', data=data)

@app.route('/projects')
def projects():
    data = load_data()
    return render_template('projects.html', data=data)

@app.route('/contact', methods=['POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        
        # Check for credentials
        if not app.config['MAIL_USERNAME'] or not app.config['MAIL_PASSWORD'] or \
           app.config['MAIL_USERNAME'] == 'your_email@gmail.com':
            flash('Email configuration incomplete. Please update .env file with valid credentials.', 'danger')
            return redirect(url_for('index', _anchor='contact'))

        # Track Interaction
        analytics = load_analytics()
        analytics['interactions']['contact_submit'] = analytics['interactions'].get('contact_submit', 0) + 1
        save_analytics(analytics)
        
        # Send Email
        try:
            data = load_data()
            recipient_email = data.get('contact', {}).get('email')
            
            if not recipient_email:
                recipient_email = app.config['MAIL_USERNAME'] # Fallback
                
            msg = Message(f"Portfolio Contact from {name}",
                          sender=app.config['MAIL_USERNAME'],
                          recipients=[recipient_email],
                          reply_to=email)
            msg.body = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
            mail.send(msg)
            flash('Message sent successfully!', 'success')
            if app.config.get('DEBUG'):
                print(f"Email sent from {name} ({email}): {message}") # Log for dev
        except Exception as e:
            import traceback
            traceback.print_exc()
            flash(f'Error sending message: {str(e)}', 'danger')
            
        return redirect(url_for('index', _anchor='contact'))

@app.route('/download_resume')
def download_resume():
    data = load_data()
    resume_link = data['profile'].get('resume_link')
    
    if resume_link:
        # Track Download
        analytics = load_analytics()
        analytics['interactions']['resume_download'] = analytics['interactions'].get('resume_download', 0) + 1
        save_analytics(analytics)
        
        return redirect(resume_link)
    else:
        flash('Resume not available.', 'warning')
        return redirect(url_for('index'))

# Admin Routes
@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Use config credentials
        if username == app.config['ADMIN_USERNAME'] and password == app.config['ADMIN_PASSWORD']:
            session['logged_in'] = True
            flash('Logged in successfully.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials.', 'danger')
            
    return render_template('login.html')

@app.route('/admin/logout')
def logout():
    session.pop('logged_in', None)
    flash('Logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/admin/dashboard', methods=['GET', 'POST'])
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    data = load_data()
    analytics = load_analytics()
    
    if request.method == 'POST':
        # Helper to save file
        def save_uploaded_file(file_key):
            if file_key in request.files:
                file = request.files[file_key]
                if file and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    return f"/static/uploads/{filename}"
            return None

        # Update Profile
        if 'update_profile' in request.form:
            data['profile']['name'] = request.form.get('name')
            data['profile']['title'] = request.form.get('title')
            data['profile']['intro'] = request.form.get('intro')
            data['profile']['bio'] = request.form.get('bio')
            
            img_path = save_uploaded_file('image_file')
            if img_path:
                data['profile']['image'] = img_path
            elif request.form.get('image'):
                data['profile']['image'] = request.form.get('image')

            resume_path = save_uploaded_file('resume_file')
            if resume_path:
                data['profile']['resume_link'] = resume_path
            elif request.form.get('resume_link'):
                data['profile']['resume_link'] = request.form.get('resume_link')
            
        # Update Skills
        elif 'update_skills' in request.form:
            skills_str = request.form.get('skills')
            # Split by comma or newline (and handle potential carriage returns)
            data['skills'] = [s.strip() for s in re.split(r'[,\n\r]+', skills_str) if s.strip()]

        # Update Education
        elif 'update_education' in request.form:
            degrees = request.form.getlist('edu_degree')
            institutions = request.form.getlist('edu_institution')
            years = request.form.getlist('edu_year')
            
            new_education = []
            for i in range(len(degrees)):
                # Check for deletion flag
                if request.form.get(f'delete_education_{i}') == '1':
                    continue
                    
                new_education.append({
                    'degree': degrees[i],
                    'institution': institutions[i],
                    'year': years[i]
                })
            data['education'] = new_education

        # Add Education
        elif 'add_education' in request.form:
            new_edu = {
                'degree': request.form.get('new_edu_degree'),
                'institution': request.form.get('new_edu_institution'),
                'year': request.form.get('new_edu_year')
            }
            if 'education' not in data:
                data['education'] = []
            data['education'].append(new_edu)
            
        # Update Contact
        elif 'update_contact' in request.form:
            data['contact']['email'] = request.form.get('email')
            data['contact']['linkedin'] = request.form.get('linkedin')
            data['contact']['github'] = request.form.get('github')
            data['contact']['twitter'] = request.form.get('twitter')
            data['contact']['instagram'] = request.form.get('instagram')
            data['contact']['location'] = request.form.get('location')
            
        # Update Projects (Edit Existing)
        elif 'update_projects' in request.form:
            new_projects = []
            i = 0
            while True:
                # Check if the title for index i exists
                title_key = f'project_title_{i}'
                if title_key not in request.form:
                    break
                
                title = request.form.get(title_key)
                desc = request.form.get(f'project_desc_{i}')
                tech = request.form.get(f'project_tech_{i}')
                github = request.form.get(f'project_github_{i}')
                
                # Handle Image
                image_path = request.form.get(f'project_image_{i}')
                file_key = f'project_image_file_{i}'
                if file_key in request.files:
                    file = request.files[file_key]
                    if file and file.filename != '' and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        image_path = f"/static/uploads/{filename}"

                # Checkbox handling
                is_featured = request.form.get(f'project_featured_{i}') == 'on'
                
                # Check for deletion flag
                if request.form.get(f'delete_project_{i}') == '1':
                    i += 1
                    continue

                new_projects.append({
                    'title': title,
                    'description': desc,
                    'technologies': tech,
                    'github_link': github,
                    'image': image_path,
                    'featured': is_featured
                })
                i += 1
            
            data['projects'] = new_projects

        # Add New Project
        elif 'add_project' in request.form:
            image_path = save_uploaded_file('new_project_image_file')
            if not image_path:
                image_path = request.form.get('new_project_image') or "https://via.placeholder.com/300x200"
                
            new_project = {
                'title': request.form.get('new_project_title'),
                'description': request.form.get('new_project_desc'),
                'technologies': request.form.get('new_project_tech'),
                'github_link': request.form.get('new_project_github'),
                'image': image_path,
                'featured': request.form.get('new_project_featured') == 'on'
            }
            data['projects'].append(new_project)

        # Update Certifications
        elif 'update_certs' in request.form:
            titles = request.form.getlist('cert_title')
            orgs = request.form.getlist('cert_org')
            dates = request.form.getlist('cert_date')
            links = request.form.getlist('cert_link')
            descs = request.form.getlist('cert_desc')
            
            new_certs = []
            for i in range(len(titles)):
                new_certs.append({
                    'title': titles[i],
                    'organization': orgs[i],
                    'date': dates[i],
                    'link': links[i],
                    'description': descs[i]
                })
            data['certifications'] = new_certs

        # Add New Certification
        elif 'add_cert' in request.form:
            new_cert = {
                'title': request.form.get('new_cert_title'),
                'organization': request.form.get('new_cert_org'),
                'date': request.form.get('new_cert_date'),
                'link': request.form.get('new_cert_link'),
                'description': request.form.get('new_cert_desc')
            }
            data['certifications'].append(new_cert)

        save_data(data)
        flash('Data updated successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('dashboard.html', data=data, analytics=analytics)


if __name__ == '__main__':
    # When running directly, use the configured debug mode
    app.run(debug=app.config.get('DEBUG', False))
