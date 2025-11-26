import streamlit as st
import json
import requests
import yaml

@st.cache_data
def load_system_prompts():
    with open("system_prompts.yaml", "r") as f:
        data = yaml.safe_load(f)
    return data.get("system_prompts", {}), data.get("voices", {})

SYSTEM_PROMPTS, ALL_VOICES = load_system_prompts()


# Configuration
API_BASE_URL = "https://api.vapi.ai"

# Load API key from config
@st.cache_data
def get_api_key():
    try:
        # Check if config.json exists
        if os.path.exists("config.json"):
            with open("config.json", "r") as f:
                config = json.load(f)
            return config["vapi_api_key"]
        else:
            # Use Streamlit secrets
            return st.secrets["vapi_api_key"]
    except FileNotFoundError:
        st.error("config.json not found. Please create it with your VAPI API key.")
        st.stop()


# VAPI API Functions
def get_assistant(assistant_id, api_key):
    url = f"{API_BASE_URL}/assistant/{assistant_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def update_assistant(assistant_id, api_key, data):
    url = f"{API_BASE_URL}/assistant/{assistant_id}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    response = requests.patch(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

def list_calls(api_key, assistant_id=None, limit=50):
    url = f"{API_BASE_URL}/call"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    params = {"limit": limit}
    if assistant_id:
        params["assistantId"] = assistant_id
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def get_call(call_id, api_key):
    url = f"{API_BASE_URL}/call/{call_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def get_tool(tool_id, api_key):
    url = f"{API_BASE_URL}/tool/{tool_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def update_tool(tool_id, api_key, data):
    url = f"{API_BASE_URL}/tool/{tool_id}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    response = requests.patch(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

# Helper function to format whitelist
def format_whitelist(numbers):
    if not numbers:
        return "  # No numbers in whitelist"
    return "\n".join([f"  {num.strip()}" for num in numbers if num.strip()])

# Helper function to inject variables into prompt
def build_system_prompt(mode, owner_name, friend_name, relationship, whitelist_numbers):
    template = SYSTEM_PROMPTS[mode]
    whitelist_formatted = format_whitelist(whitelist_numbers)
    
    prompt = template.replace("{owner_name}", owner_name)
    prompt = prompt.replace("{friend_name}", friend_name)
    prompt = prompt.replace("{relationship}", relationship)
    prompt = prompt.replace("{whitelist}", whitelist_formatted)
    
    return prompt

# Phone number management functions
def list_phone_numbers(api_key):
    url = f"{API_BASE_URL}/phone-number"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def get_phone_number(phone_number_id, api_key):
    url = f"{API_BASE_URL}/phone-number/{phone_number_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def create_phone_number(api_key, data):
    url = f"{API_BASE_URL}/phone-number"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

def update_phone_number(phone_number_id, api_key, data):
    url = f"{API_BASE_URL}/phone-number/{phone_number_id}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    response = requests.patch(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

# Streamlit App
def main():
    st.set_page_config(page_title="Assistant UI", page_icon="📞", layout="wide")
    
    st.title("📞 Assistant UI")
    st.markdown("---")
    
    # Initialize session state
    if 'assistant_id' not in st.session_state:
        st.session_state.assistant_id = ""
    if 'owner_name' not in st.session_state:
        st.session_state.owner_name = "Lisa"
    if 'friend_name' not in st.session_state:
        st.session_state.friend_name = "Amanda"
    if 'whitelist_numbers' not in st.session_state:
        st.session_state.whitelist_numbers = ["+447700900123", "+61400111222", "+212637064581"]
    if 'current_mode' not in st.session_state:
        st.session_state.current_mode = "Trusting"
    if 'selected_voice_provider' not in st.session_state:
        st.session_state.selected_voice_provider = "vapi"
    if 'selected_voice_id' not in st.session_state:
        st.session_state.selected_voice_id = "Kylie"  # Rachel default
    if 'transfer_tool_id' not in st.session_state:
        st.session_state.transfer_tool_id = "3234284e-b277-4dc5-a614-edfe19394ff5"
    if 'owner_phone' not in st.session_state:
        st.session_state.owner_phone = "+46702657787"
    if 'friend_phone' not in st.session_state:
        st.session_state.friend_phone = "+46768364130"
    if 'selected_language' not in st.session_state:
        st.session_state.selected_language = "English"
    if 'relationship' not in st.session_state:
        st.session_state.relationship = "sister"
    
    # Get API key
    api_key = get_api_key()
    
    # Sidebar - Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Assistant ID
        assistant_id = st.text_input(
            "Assistant ID",
            value=st.session_state.assistant_id,
            help="Enter your VAPI assistant ID"
        )
        st.session_state.assistant_id = assistant_id
        
        st.markdown("---")
        
        # Load current assistant
        if st.button("🔄 Load Assistant", use_container_width=True):
            if not assistant_id:
                st.error("Please enter an Assistant ID")
            else:
                try:
                    with st.spinner("Loading assistant..."):
                        assistant = get_assistant(assistant_id, api_key)
                        
                        # Cache the assistant data
                        st.session_state.cached_assistant = assistant
                        st.session_state.cached_assistant_id = assistant_id
                        
                        st.success("✅ Assistant loaded successfully!")
                        
                        # Try to extract current mode from system prompt
                        if 'model' in assistant and 'messages' in assistant['model']:
                            messages = assistant['model']['messages']
                            if messages and len(messages) > 0:
                                current_prompt = messages[0].get('content', '')
                                # st.info(f"Current system prompt length: {len(current_prompt)} characters")
                except Exception as e:
                    st.error(f"❌ Error loading assistant: {str(e)}")
    
    # Main content
    if not assistant_id:
        st.warning("👈 Please enter your Assistant ID in the sidebar to get started")
        return

    # Create tabs
    # tab1, tab2 = st.tabs(["⚙️ Assistant Settings", "📞 Call History"])
    tab1, tab2, tab3 = st.tabs(["⚙️ Assistant Settings", "📞 Call History", "📱 Phone Numbers"])
    
    with tab1:
        # Owner and Friend Configuration Section
        st.subheader("👤 Contact Information")
        
        # Language selection
        language = st.radio(
            "🌍 Language",
            options=["English", "Swedish"],
            horizontal=True,
            key="language_selector"
        )
        st.session_state.selected_language = language

        st.markdown("---")
        
        config_col1, config_col2 = st.columns(2)
        
        with config_col1:
            st.write("**Owner Details:**")
            owner_name = st.text_input(
                "Owner Name",
                value=st.session_state.owner_name,
                help="The person who owns this assistant",
                key="owner_name_input"
            )
            st.session_state.owner_name = owner_name
            
            owner_phone = st.text_input(
                "Owner Phone Number",
                value=st.session_state.owner_phone,
                help="Phone number to transfer calls to the owner",
                placeholder="+46702657787",
                key="owner_phone_input"
            )
            st.session_state.owner_phone = owner_phone
        
        with config_col2:
            st.write("**Friend Details:**")
            friend_name = st.text_input(
                "Friend Name",
                value=st.session_state.friend_name,
                help="Friend's name (e.g., Amanda)",
                key="friend_name_input"
            )
            st.session_state.friend_name = friend_name
            
            relationship = st.text_input(
                "Relationship to Owner",
                value=st.session_state.relationship,
                help="e.g., sister, brother, friend, colleague",
                placeholder="sister",
                key="relationship_input"
            )
            st.session_state.relationship = relationship
            
            friend_phone = st.text_input(
                "Friend Phone Number",
                value=st.session_state.friend_phone,
                help="Phone number to transfer calls to the friend",
                placeholder="+46768364130",
                key="friend_phone_input"
            )
            st.session_state.friend_phone = friend_phone
        
        st.markdown("---")
    
        # Two columns layout
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("🎭 Select Mode")

            # Filter modes based on selected language
            if st.session_state.selected_language == "English":
                available_modes = ["Trusting", "Strict"]
                mode_suffix = ""
            else:  # Swedish
                available_modes = ["TrustingSv", "StrictSv"]
                mode_suffix = "Sv"

            # Map display names to actual mode keys
            display_to_key = {
                "Trusting": "Trusting",
                "Strict": "Strict",
                "TrustingSv": "TrustingSv",
                "StrictSv": "StrictSv"
            }

            # Create display names
            if st.session_state.selected_language == "English":
                mode_display_names = ["Trusting", "Strict"]
            else:
                mode_display_names = ["TrustingSv", "StrictSv"]

            # Get current mode display name
            current_mode_key = st.session_state.current_mode
            if current_mode_key in available_modes:
                if st.session_state.selected_language == "Swedish":
                    current_display = f"Trusting (Swedish)" if "Trusting" in current_mode_key else "Strict (Swedish)"
                else:
                    current_display = current_mode_key
                try:
                    mode_index = mode_display_names.index(current_display)
                except ValueError:
                    mode_index = 0
            else:
                mode_index = 0

            selected_mode = st.selectbox(
                "Choose assistant mode",
                options=mode_display_names,
                index=mode_index,
                help="Different conversation styles for your assistant"
            )

            # Convert display name back to key
            st.session_state.current_mode = display_to_key[selected_mode]

            # Show mode description
            mode_descriptions = {
                "Trusting": "Friendly and trusting conversation style",
                "Strict": "Professional and strict screening protocol",
                "TrustingSv": "Vänlig och tillitsfull samtalsstil",
                "StrictSv": "Professionell och strikt screeningprotokoll"
            }
            st.info(mode_descriptions[selected_mode])
        
        with col2:
            st.subheader("📋 Whitelist Numbers")
            
            # Display current whitelist
            st.text_area(
                "Current whitelist (one per line)",
                value="\n".join(st.session_state.whitelist_numbers),
                height=150,
                disabled=True
            )
            
            # Add/Remove numbers
            with st.expander("✏️ Edit Whitelist"):
                new_number = st.text_input(
                    "Add new number",
                    placeholder="+1234567890",
                    help="Enter phone number with country code (e.g., +1234567890)"
                )
                
                if st.button("➕ Add Number"):
                    if new_number and new_number not in st.session_state.whitelist_numbers:
                        st.session_state.whitelist_numbers.append(new_number)
                        st.success(f"Added {new_number}")
                        st.rerun()
                    elif new_number in st.session_state.whitelist_numbers:
                        st.warning("Number already in whitelist")
                
                st.markdown("---")
                
                # Remove number
                if st.session_state.whitelist_numbers:
                    number_to_remove = st.selectbox(
                        "Remove number",
                        options=st.session_state.whitelist_numbers
                    )
                    
                    if st.button("➖ Remove Number"):
                        st.session_state.whitelist_numbers.remove(number_to_remove)
                        st.success(f"Removed {number_to_remove}")
                        st.rerun()
        
        st.markdown("---")
        
        # Voice selection
        st.subheader("🎤 Select Voice")

        # Get voices based on selected language
        language_key = "english" if st.session_state.selected_language == "English" else "swedish"
        VOICE_OPTIONS = ALL_VOICES.get(language_key, {})

        col_voice1, col_voice2 = st.columns(2)

        with col_voice1:
            voice_provider = st.selectbox(
                "Voice Provider",
                options=list(VOICE_OPTIONS.keys()),
                index=list(VOICE_OPTIONS.keys()).index(st.session_state.selected_voice_provider) if st.session_state.selected_voice_provider in VOICE_OPTIONS.keys() else 0,
                help="Select your TTS provider"
            )
            st.session_state.selected_voice_provider = voice_provider

        with col_voice2:
            available_voices = VOICE_OPTIONS[voice_provider]
            voice_names = [v["name"] for v in available_voices]
            
            # Find current voice name
            current_voice_name = next(
                (v["name"] for v in available_voices if v["voiceId"] == st.session_state.selected_voice_id),
                voice_names[0] if voice_names else None
            )
            
            if voice_names:
                selected_voice_name = st.selectbox(
                    "Voice",
                    options=voice_names,
                    index=voice_names.index(current_voice_name) if current_voice_name in voice_names else 0,
                    help="Select the voice for your assistant"
                )
                
                # Get voice ID from name
                st.session_state.selected_voice_id = next(
                    v["voiceId"] for v in available_voices if v["name"] == selected_voice_name
                )
            else:
                st.warning("No voices available for this provider")

        st.info(f"Selected: {voice_provider} - {st.session_state.selected_voice_id}")
    
    with tab2:
        st.subheader("📞 Call History")
        
        # Filters
        col_filter1, col_filter2, col_filter3 = st.columns([2, 1, 1])
        
        with col_filter1:
            filter_option = st.radio(
                "Filter calls",
                options=["All Calls"],
                horizontal=True
            )
        
        with col_filter2:
            limit = st.selectbox("Show", options=[10, 25, 50, 100], index=1)
        
        with col_filter3:
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()
        
        # Fetch calls
        try:
            with st.spinner("Loading call history..."):
                if filter_option == "This Assistant Only":
                    calls = list_calls(api_key, assistant_id=assistant_id, limit=limit)
                else:
                    calls = list_calls(api_key, limit=limit)
            
            if not calls:
                st.info("No calls found")
            else:
                st.success(f"Found {len(calls)} calls")
                
                # Display calls
                for call in calls:
                    with st.expander(
                        f"📞 {call.get('customer', {}).get('number', 'Unknown')} - "
                        f"{call.get('createdAt', 'N/A')[:16]}"
                    ):
                        # Call details in columns
                        detail_col1, detail_col2 = st.columns(2)
                        
                        with detail_col1:
                            st.write("**Call Information:**")
                            st.write(f"📱 **Phone:** {call.get('customer', {}).get('number', 'N/A')}")
                            st.write(f"🆔 **Call ID:** {call.get('id', 'N/A')}")
                            st.write(f"📅 **Created:** {call.get('createdAt', 'N/A')}")
                            st.write(f"🚀 **Started:** {call.get('startedAt', 'Not started')}")
                            st.write(f"🛑 **Ended:** {call.get('endedAt', 'Not ended')}")
                            
                            # Calculate duration if available
                            if call.get('startedAt') and call.get('endedAt'):
                                from datetime import datetime
                                start = datetime.fromisoformat(call['startedAt'].replace('Z', '+00:00'))
                                end = datetime.fromisoformat(call['endedAt'].replace('Z', '+00:00'))
                                duration = (end - start).total_seconds()
                                st.write(f"⏱️ **Duration:** {int(duration)} seconds")
                        
                        with detail_col2:
                            st.write("**Status & Type:**")
                            st.write(f"📊 **Status:** {call.get('status', 'N/A')}")
                            st.write(f"📞 **Type:** {call.get('type', 'N/A')}")
                            
                            if 'cost' in call:
                                st.write(f"💰 **Cost:** ${call.get('cost', 0)}")
                            
                            if 'endedReason' in call:
                                st.write(f"🔚 **End Reason:** {call.get('endedReason', 'N/A')}")
                        
                        # Transcript section
                        if 'transcript' in call and call['transcript']:
                            st.markdown("---")
                            st.write("**📝 Transcript:**")
                            st.text_area(
                                "Conversation",
                                value=call['transcript'],
                                height=200,
                                disabled=True,
                                key=f"transcript_{call['id']}"
                            )
                        
                        # Analysis section
                        if 'analysis' in call and call['analysis']:
                            st.markdown("---")
                            st.write("**📊 Analysis:**")
                            st.json(call['analysis'])
                        
                        # View full details
                        # if st.button("🔍 View Full Details", key=f"details_{call['id']}"):
                        #     st.json(call)
        
        except Exception as e:
            st.error(f"❌ Error loading call history: {str(e)}")
        
    
    # Phone Numbers content
    with tab3:
        st.subheader("📱 Phone Numbers Management")
        
        # Buttons row
        col_btn1, col_btn2 = st.columns([1, 4])
        
        with col_btn1:
            if st.button("🔄 Refresh", use_container_width=True, key="refresh_phones"):
                st.rerun()
        
        # Fetch phone numbers
        try:
            with st.spinner("Loading phone numbers..."):
                phone_numbers = list_phone_numbers(api_key)
            
            if not phone_numbers:
                st.info("No phone numbers found. Create one below!")
            else:
                st.success(f"Found {len(phone_numbers)} phone number(s)")
                
                # Display phone numbers
                for phone in phone_numbers:
                    with st.expander(
                        f"📱 {phone.get('number', 'N/A')} - "
                        f"{'✅ Assigned' if phone.get('assistantId') else '⚪ Unassigned'}"
                    ):
                        # Phone details
                        detail_col1, detail_col2 = st.columns(2)
                        
                        with detail_col1:
                            st.write("**Phone Details:**")
                            st.write(f"📱 **Number:** {phone.get('number', 'N/A')}")
                            st.write(f"🆔 **Phone ID:** {phone.get('id', 'N/A')}")
                            st.write(f"🏷️ **Name:** {phone.get('name', 'N/A')}")
                            st.write(f"📅 **Created:** {phone.get('createdAt', 'N/A')[:10]}")
                        
                        with detail_col2:
                            st.write("**Assignment:**")
                            current_assistant_id = phone.get('assistantId', '')
                            
                            if current_assistant_id:
                                st.write(f"✅ **Assigned to:** {current_assistant_id}")
                                if current_assistant_id == assistant_id:
                                    st.success("This is your current assistant!")
                            else:
                                st.write("⚪ **Not assigned to any assistant**")
                        
                        st.markdown("---")
                        
                        # Assign/Unassign assistant
                        assign_col1, assign_col2 = st.columns(2)
                        
                        with assign_col1:
                            if st.button(
                                f"✅ Assign to Current Assistant",
                                key=f"assign_{phone['id']}",
                                use_container_width=True,
                                disabled=(current_assistant_id == assistant_id)
                            ):
                                try:
                                    update_data = {"assistantId": assistant_id}
                                    update_phone_number(phone['id'], api_key, update_data)
                                    st.success("Phone number assigned!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                        
                        with assign_col2:
                            if st.button(
                                f"❌ Unassign",
                                key=f"unassign_{phone['id']}",
                                use_container_width=True,
                                disabled=(not current_assistant_id)
                            ):
                                try:
                                    update_data = {"assistantId": None}
                                    update_phone_number(phone['id'], api_key, update_data)
                                    st.success("Phone number unassigned!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
    
        except Exception as e:
            st.error(f"❌ Error loading phone numbers: {str(e)}")
        
        # Create new phone number section
        st.markdown("---")
        st.subheader("➕ Import Twilio Phone Number")

        with st.expander("Import a phone number from Twilio", expanded=False):
            st.info("📝 You need to have a Twilio account and phone number already purchased.")
            
            create_col1, create_col2 = st.columns(2)
            
            with create_col1:
                twilio_account_sid = st.text_input(
                    "Twilio Account SID",
                    placeholder="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                    key="twilio_sid",
                    type="password"
                )
                
                twilio_phone_number = st.text_input(
                    "Phone Number",
                    placeholder="+1234567890",
                    help="Your Twilio phone number in E.164 format",
                    key="twilio_number"
                )
            
            with create_col2:
                twilio_auth_token = st.text_input(
                    "Twilio Auth Token",
                    placeholder="your_auth_token",
                    key="twilio_token",
                    type="password"
                )
                
                new_phone_name = st.text_input(
                    "Name (optional)",
                    placeholder="My Business Line",
                    key="new_phone_name"
                )
            
            assign_to_current = st.checkbox(
                "Assign to current assistant",
                value=True,
                key="assign_new_phone"
            )
            
            if st.button("🚀 Import Twilio Number", use_container_width=True, type="primary", key="create_phone_btn"):
                if not twilio_account_sid or not twilio_auth_token or not twilio_phone_number:
                    st.error("❌ Please fill in all required fields: Account SID, Auth Token, and Phone Number")
                else:
                    try:
                        with st.spinner("Importing phone number from Twilio..."):
                            create_data = {
                                "provider": "twilio",
                                "number": twilio_phone_number,
                                "twilioAccountSid": twilio_account_sid,
                                "twilioAuthToken": twilio_auth_token
                            }
                            
                            if new_phone_name:
                                create_data["name"] = new_phone_name
                            
                            if assign_to_current and assistant_id:
                                create_data["assistantId"] = assistant_id
                            
                            result = create_phone_number(api_key, create_data)
                            
                            st.success(f"✅ Phone number imported: {result.get('number', 'N/A')}")
                            st.balloons()
                            st.rerun()
                            
                    except Exception as e:
                        st.error(f"❌ Error importing phone number: {str(e)}")
                        st.exception(e)
    
    
    # Preview section
    st.subheader("👁️ System Prompt Preview")
    
    preview_prompt = build_system_prompt(
        selected_mode,
        st.session_state.owner_name,
        st.session_state.friend_name,
        st.session_state.relationship,
        st.session_state.whitelist_numbers
    )
    
    with st.expander("View full system prompt", expanded=False):
        st.code(preview_prompt, language="text")
    
    st.info(f"📊 Prompt length: {len(preview_prompt)} characters | {len(preview_prompt.split())} words")
    # Update button
    st.markdown("---")
    
    col_update1, col_update2, col_update3 = st.columns([2, 1, 2])
    
    with col_update2:
        if st.button("🚀 Update Assistant", use_container_width=True, type="primary"):
            # Check if we have cached assistant data
            if 'cached_assistant' not in st.session_state:
                st.error("❌ Please click 'Load Assistant' first to fetch current configuration")
            else:
                try:
                    with st.spinner("Updating assistant and transfer tool..."):
                        # Build the complete system prompt
                        system_prompt = build_system_prompt(
                            st.session_state.current_mode,
                            st.session_state.owner_name,
                            st.session_state.friend_name,
                            st.session_state.relationship,
                            st.session_state.whitelist_numbers
                        )
                        
                        # Use cached assistant data
                        current_assistant = st.session_state.cached_assistant
                        
                        # Prepare assistant update payload
                        assistant_update_data = {
                            "model": {
                                **current_assistant.get("model", {}),
                                "messages": [
                                    {
                                        "role": "system",
                                        "content": system_prompt
                                    }
                                ]
                            },
                            "voice": {
                                "provider": st.session_state.selected_voice_provider,
                                "voiceId": st.session_state.selected_voice_id
                            },
                            "transcriber": {
                                "provider": "deepgram",
                                "model": "nova-2" if st.session_state.selected_language == "English" else "nova-3",
                                "language": "en" if st.session_state.selected_language == "English" else "Sv-SE"
                            }
                        }
                        
                        # Update assistant
                        result = update_assistant(assistant_id, api_key, assistant_update_data)
                        
                        # Update cache with new data
                        st.session_state.cached_assistant = result
                        
                        # Update transfer tool
                        # Update transfer tool
                        # First, get the current tool to preserve its structure
                        try:
                            current_tool = get_tool(st.session_state.transfer_tool_id, api_key)
                            
                            # Only update the fields we want to change
                            tool_update_data = {
                                "destinations": [
                                    {
                                        "type": "number",
                                        "number": st.session_state.owner_phone,
                                        "message": f"I am forwarding your call to {st.session_state.owner_name}. Please stay on the line please.",
                                        "description": f"Use this destination when asked to forward the call to {st.session_state.owner_name}"
                                    },
                                    {
                                        "type": "number",
                                        "number": st.session_state.friend_phone,
                                        "message": f"I am forwarding your call to {st.session_state.owner_name}'s {st.session_state.relationship} {st.session_state.friend_name}. Please stay on the line please.",
                                        "description": f"Use this destination when asked to forward the call to {st.session_state.owner_name}'s {st.session_state.relationship} {st.session_state.friend_name}"
                                    }
                                ]
                            }
                            
                            # Only add function name and description if the tool has a function field
                            if 'function' in current_tool:
                                tool_update_data['function'] = {
                                    **current_tool.get('function', {}),
                                    'name': f"transfer_call_tool_to_{st.session_state.owner_name}",
                                    'description': f"Use this function to transfer the call. Only use it when following instructions that explicitly ask you to use the transferCall function. DO NOT call this function unless you are instructed to do so."
                                }
                            
                            tool_result = update_tool(st.session_state.transfer_tool_id, api_key, tool_update_data)
                            
                        except Exception as tool_error:
                            st.warning(f"⚠️ Could not update transfer tool: {str(tool_error)}")
                            # Don't fail the whole update if just the tool fails
                        
                        st.success("✅ Assistant and transfer tool updated successfully!")
                        st.balloons()
                        
                except Exception as e:
                    st.error(f"❌ Error updating: {str(e)}")
                    st.exception(e)

if __name__ == "__main__":
    main()