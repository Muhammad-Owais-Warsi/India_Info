from flask import Flask, jsonify, request, render_template
import pandas as pd
from typing import Dict, List
import json

app = Flask(__name__)

# Global variable declaration at the module level
df = None

# Load and prepare data
def load_data() -> pd.DataFrame:
    try:
        df = pd.read_csv('panchayat_data_with_members.csv',
                        on_bad_lines='skip',
                        header=0)  # Use first row as header
        
        # Rename columns to match our API
        df.columns = ['state_code', 'state', 'district_code', 'district', 
                     'taluk_code', 'taluk', 'village_code', 'village',
                     'member_id', 'name', 'phone', 'email', 'role']
        
        # Clean the data
        code_columns = ['state_code', 'district_code', 'taluk_code', 'village_code']
        for col in code_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Drop rows with NaN values in critical columns
        df = df.dropna(subset=code_columns)
        
        # Convert codes to integers
        for col in code_columns:
            df[col] = df[col].astype(int)
            
        return df
    
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        return pd.DataFrame(columns=['state_code', 'state', 'district_code', 'district', 
                                   'taluk_code', 'taluk', 'village_code', 'village',
                                   'member_id', 'name', 'phone', 'email', 'role'])

# Initialize data
df = load_data()

# Main route to serve the HTML
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/states', methods=['GET'])
def get_states():
    """Get list of all states"""
    states = df[['state_code', 'state']].drop_duplicates().to_dict('records')
    return jsonify(states)

@app.route('/api/districts/<state_code>', methods=['GET'])
def get_districts(state_code):
    """Get districts for a given state"""
    try:
        state_code = int(state_code)
        districts = df[df['state_code'] == state_code][['district_code', 'district']].drop_duplicates().to_dict('records')
        return jsonify(districts)
    except:
        return jsonify([])

@app.route('/api/taluks/<district_code>', methods=['GET'])
def get_taluks(district_code):
    """Get taluks for a given district"""
    try:
        district_code = int(district_code)
        taluks = df[df['district_code'] == district_code][['taluk_code', 'taluk']].drop_duplicates().to_dict('records')
        return jsonify(taluks)
    except:
        return jsonify([])

@app.route('/api/villages/<taluk_code>', methods=['GET'])
def get_villages(taluk_code):
    """Get villages for a given taluk"""
    try:
        taluk_code = int(taluk_code)
        villages = df[df['taluk_code'] == taluk_code][['village_code', 'village']].drop_duplicates().to_dict('records')
        return jsonify(villages)
    except:
        return jsonify([])

@app.route('/api/members', methods=['GET'])
def get_members():
    """Get members based on query parameters"""
    try:
        filters = {}
        
        # Add filters based on query parameters
        if request.args.get('village_code'):
            filters['village_code'] = int(request.args.get('village_code'))
        
        # Apply filters
        filtered_df = df
        for key, value in filters.items():
            filtered_df = filtered_df[filtered_df[key] == value]

        # Get members
        members = filtered_df[[
            'name', 'role', 'phone', 'email', 'village', 'taluk', 'district', 'state'
        ]].to_dict('records')

        return jsonify(members)
    except Exception as e:
        print(f"Error in get_members: {str(e)}")
        return jsonify([])

@app.route('/api/members/add', methods=['POST'])
def add_member():
    global df  # Now correctly declaring global
    try:
        data = request.json
        
        # Get the location details based on village_code
        village_data = df[df['village_code'] == int(data['village_code'])].iloc[0]
        
        # Create new member row
        new_member = {
            'state_code': village_data['state_code'],
            'state': village_data['state'],
            'district_code': village_data['district_code'],
            'district': village_data['district'],
            'taluk_code': village_data['taluk_code'],
            'taluk': village_data['taluk'],
            'village_code': int(data['village_code']),
            'village': village_data['village'],
            'member_id': df['member_id'].max() + 1,  # Generate new ID
            'name': data['name'],
            'phone': data['phone'],
            'email': data['email'],
            'role': data['role']
        }
        
        # Append to DataFrame
        df = pd.concat([df, pd.DataFrame([new_member])], ignore_index=True)
        
        # Save to CSV
        df.to_csv('panchayat_data_with_members.csv', index=False)
        
        return jsonify({'success': True, 'message': 'Member added successfully'})
    
    except Exception as e:
        print(f"Error adding member: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 400

if __name__ == '__main__':
    # Print some debug information
    print(f"Total records loaded: {len(df)}")
    print(f"Unique states: {df['state'].nunique()}")
    print(f"Unique districts: {df['district'].nunique()}")
    print(f"Sample data:")
    print(df.head())
    
    # Run the app
    app.run(debug=True)