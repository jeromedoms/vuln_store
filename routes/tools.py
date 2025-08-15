from flask import Blueprint, render_template, request, jsonify, send_file
import hashlib
import re
from io import BytesIO
from werkzeug.utils import secure_filename

tools_bp = Blueprint('tools', __name__)

@tools_bp.route('/dan')
def file_info():
    return render_template('file_info.html')

@tools_bp.route('/dan/calculate', methods=['POST'])
def calculate_file_hashes():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Read file content
        file_content = file.read()
        
        # Calculate hashes
        sha256_hash = hashlib.sha256(file_content).hexdigest()
        sha1_hash = hashlib.sha1(file_content).hexdigest()
        md5_hash = hashlib.md5(file_content).hexdigest()
        
        return jsonify({
            'success': True,
            'hashes': {
                'sha256': sha256_hash,
                'sha1': sha1_hash,
                'md5': md5_hash
            },
            'file_info': {
                'name': secure_filename(file.filename),
                'size': len(file_content)
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tools_bp.route('/bog')
def gen():
    return render_template('wordlist_generator.html')

@tools_bp.route('/bog/generate', methods=['POST'])
def generator():
    text = request.form['text']
    group_size = int(request.form['group_size'])
    
    # Process text - remove non-alphanumeric characters and convert to lowercase
    cleaned_text = re.sub(r'[^a-zA-Z0-9]', '', text).lower()
    
    # Create groups
    grouped_words = [cleaned_text[i:i+group_size] 
                   for i in range(0, len(cleaned_text), group_size)]
    
    # Filter out empty groups (in case the last group is incomplete)
    grouped_words = [group for group in grouped_words if group]
    
    # Join with LF only (\n) - this ensures consistent line endings
    wordlist_content = '\n'.join(grouped_words)
    
    return jsonify({
        'content': wordlist_content,  # Send the exact content string
        'count': len(grouped_words),
        'sample': grouped_words[:5]
    })

@tools_bp.route('/bog/download', methods=['POST'])
def download_wordlist():
    content = request.json['content']  # Receive the exact content from frontend
    
    # Create file with the exact content (preserving LF-only endings)
    file_data = BytesIO()
    file_data.write(content.encode('utf-8'))
    file_data.seek(0)
    
    return send_file(
        file_data,
        mimetype='text/plain',
        as_attachment=True,
        download_name='wordlist.txt'
    )