import streamlit as st
from styles import apply_custom_styles
from pages.accueil import display_accueil

def main():
    apply_custom_styles()
    display_accueil()

if __name__ == "__main__":
    main()
