from supabase import create_client
# from django.conf import settings

# Initialize Supabase client
supabase = create_client("https://sryesoktrkolkclrolcf.supabase.co", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNyeWVzb2t0cmtvbGtjbHJvbGNmIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0MTcyOTkyNCwiZXhwIjoyMDU3MzA1OTI0fQ.zurJ0zO9A5m-Y-MmZkvgMOls7TVN2KUWLgwotnfUh18")

def get_supabase_client():
    return supabase