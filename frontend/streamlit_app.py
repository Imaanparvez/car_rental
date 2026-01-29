def recommendations_page():
    st.title("🔍 AI Car Recommendations")

    st.markdown("### Select a category")

    st.write("")  # spacing

    # CSS for hover dropdown
    st.markdown("""
        <style>
        .tile {
            position: relative;
            width: 100%;
            height: 160px;
            border-radius: 20px;
            background-size: cover;
            background-position: center;
            margin-bottom: 30px;
            cursor: pointer;
            border: 3px solid white;
            transition: transform 0.2s ease;
        }
        .tile:hover {
            transform: scale(1.03);
        }
        .dropdown {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            background: rgba(0,0,0,0.75);
            border-radius: 20px;
            padding: 15px;
            display: none;
        }
        .tile:hover .dropdown {
            display: block;
        }
        .dropdown button {
            width: 100%;
            margin-top: 10px;
            color: white !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Utility to load image
    def load_b64(path):
        import base64
        try:
            return base64.b64encode(open(path, "rb").read()).decode()
        except:
            return ""

    # Images for tiles
    brand_bg = load_b64("assets/brand.jpg")
    fuel_bg = load_b64("assets/fuel.jpg")
    body_bg = load_b64("assets/body.jpg")
    trans_bg = load_b64("assets/transmission.jpg")

    # Tile options
    brand_options = ["Toyota", "Honda", "Hyundai", "BMW"]
    fuel_options = ["Petrol", "Diesel", "Electric"]
    body_options = ["SUV", "Sedan", "Hatchback"]
    trans_options = ["Manual", "Automatic"]

    # Renderer
    def tile(col, label, bg, options, filter_key):
        with col:
            st.markdown(
                f"""
                <div class="tile" style="background-image:url('data:image/jpeg;base64,{bg}')">
                    <div class="dropdown">
                        <h4 style="color:white; text-align:center;">{label}</h4>
                """,
                unsafe_allow_html=True
            )

            for opt in options:
                if st.button(f"{opt}", key=f"{filter_key}_{opt}"):
                    st.session_state["filters"] = {filter_key: opt}
                    st.session_state["page"] = "book"
                    st.rerun()

            st.markdown("</div></div>", unsafe_allow_html=True)

    # Row 1
    c1, c2 = st.columns(2)
    tile(c1, "Brand", brand_bg, brand_options, "Brand")
    tile(c2, "Fuel Type", fuel_bg, fuel_options, "Fuel_Type")

    # Row 2
    c3, c4 = st.columns(2)
    tile(c3, "Body Type", body_bg, body_options, "Body_Type")
    tile(c4, "Transmission", trans_bg, trans_options, "Transmission")


