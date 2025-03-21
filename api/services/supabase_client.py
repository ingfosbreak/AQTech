from supabase import create_client
from django.conf import settings

# Initialize Supabase client
supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def get_supabase_client():
    return supabase