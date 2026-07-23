import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import os
import sys
from PIL import Image, ImageTk
import webbrowser
import shutil
import subprocess

# Try importing barcode library
try:
    import barcode
    from barcode.writer import ImageWriter
    BARCODE_AVAILABLE = True
except ImportError:
    BARCODE_AVAILABLE = False

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class BarcodeGeneratorApp:
    def __init__(self):
        # Main window - larger size
        self.window = ctk.CTk()
        self.window.title("Barcode Generator & Checker Pro")
        self.window.geometry("900x1000")
        self.window.minsize(800, 900)
        
        # Center the window
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
        
        if not BARCODE_AVAILABLE:
            self.show_installation_required()
            return
        
        # Create main notebook (tab view)
        self.create_tabs()
        
        # Variables
        self.current_barcode_path = None
        self.current_data = None
        self.history = []
        self.verification_history = []
        
        # Bind Enter key
        self.link_entry.bind('<Return>', lambda event: self.generate_barcode())
        self.verify_entry.bind('<Return>', lambda event: self.verify_barcode_from_input())
    
    def create_tabs(self):
        """Create the main tab view"""
        self.tabview = ctk.CTkTabview(self.window, width=850, height=950)
        self.tabview.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Add tabs
        self.tabview.add("📊 Generate")
        self.tabview.add("✅ Verify")
        self.tabview.add("📋 History")
        self.tabview.add("⚙️ Settings")
        
        # Setup each tab
        self.setup_generate_tab()
        self.setup_verify_tab()
        self.setup_history_tab()
        self.setup_settings_tab()
    
    def setup_generate_tab(self):
        """Setup the generate barcode tab"""
        generate_tab = self.tabview.tab("📊 Generate")
        
        # Main container with scrollbar
        main_container = ctk.CTkScrollableFrame(generate_tab)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_frame = ctk.CTkFrame(main_container)
        title_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            title_frame,
            text="🔲 Generate Barcode",
            font=("Arial", 28, "bold")
        ).pack(pady=5)
        
        ctk.CTkLabel(
            title_frame,
            text="Enter your data and customize the barcode",
            font=("Arial", 14)
        ).pack()
        
        # === INPUT SECTION ===
        input_frame = ctk.CTkFrame(main_container)
        input_frame.pack(pady=10, fill="x")
        
        ctk.CTkLabel(
            input_frame,
            text="📝 Data to encode:",
            font=("Arial", 15, "bold")
        ).pack(pady=(10, 5), anchor="w", padx=10)
        
        self.link_entry = ctk.CTkEntry(
            input_frame,
            height=50,
            placeholder_text="Enter text, numbers, or URL...",
            font=("Arial", 15)
        )
        self.link_entry.pack(pady=5, padx=10, fill="x")
        
        # === OPTIONS SECTION ===
        options_frame = ctk.CTkFrame(main_container)
        options_frame.pack(pady=10, fill="x")
        
        # Row 1: Barcode Type
        type_frame = ctk.CTkFrame(options_frame)
        type_frame.pack(side="left", padx=10, fill="x", expand=True)
        
        ctk.CTkLabel(
            type_frame,
            text="📊 Barcode Type:",
            font=("Arial", 14, "bold")
        ).pack(pady=5)
        
        self.barcode_type = ctk.CTkComboBox(
            type_frame,
            values=["CODE128", "EAN-13", "EAN-8", "UPC-A", "Code39", "ISBN-10"],
            width=200,
            height=40,
            font=("Arial", 14)
        )
        self.barcode_type.pack(pady=5)
        self.barcode_type.set("CODE128")
        
        # Row 2: Size Control
        size_frame = ctk.CTkFrame(options_frame)
        size_frame.pack(side="right", padx=10, fill="x", expand=True)
        
        ctk.CTkLabel(
            size_frame,
            text="📏 Barcode Size:",
            font=("Arial", 14, "bold")
        ).pack(pady=5)
        
        size_control_frame = ctk.CTkFrame(size_frame)
        size_control_frame.pack(pady=5)
        
        self.size_slider = ctk.CTkSlider(
            size_control_frame,
            from_=0.2,
            to=2.0,
            number_of_steps=18,
            width=180,
            height=25
        )
        self.size_slider.pack(side="left", padx=10)
        self.size_slider.set(1.0)
        
        self.size_label = ctk.CTkLabel(
            size_control_frame,
            text="1.0x",
            font=("Arial", 14, "bold"),
            width=50
        )
        self.size_label.pack(side="left", padx=5)
        
        self.size_slider.configure(command=lambda val: self.size_label.configure(text=f"{float(val):.1f}x"))
        
        # === ADVANCED OPTIONS ===
        advanced_frame = ctk.CTkFrame(main_container)
        advanced_frame.pack(pady=10, fill="x")
        
        # Bar Height
        height_frame = ctk.CTkFrame(advanced_frame)
        height_frame.pack(side="left", padx=10, fill="x", expand=True)
        
        ctk.CTkLabel(
            height_frame,
            text="📐 Bar Height:",
            font=("Arial", 13, "bold")
        ).pack(pady=5)
        
        self.height_slider = ctk.CTkSlider(
            height_frame,
            from_=10,
            to=40,
            number_of_steps=30,
            width=150
        )
        self.height_slider.pack(pady=5)
        self.height_slider.set(20)
        
        self.height_label = ctk.CTkLabel(
            height_frame,
            text="20",
            font=("Arial", 13)
        )
        self.height_label.pack()
        
        self.height_slider.configure(command=lambda val: self.height_label.configure(text=f"{int(float(val))}"))
        
        # Font Size
        font_frame = ctk.CTkFrame(advanced_frame)
        font_frame.pack(side="right", padx=10, fill="x", expand=True)
        
        ctk.CTkLabel(
            font_frame,
            text="🔤 Text Size:",
            font=("Arial", 13, "bold")
        ).pack(pady=5)
        
        self.font_slider = ctk.CTkSlider(
            font_frame,
            from_=8,
            to=24,
            number_of_steps=16,
            width=150
        )
        self.font_slider.pack(pady=5)
        self.font_slider.set(12)
        
        self.font_label = ctk.CTkLabel(
            font_frame,
            text="12",
            font=("Arial", 13)
        )
        self.font_label.pack()
        
        self.font_slider.configure(command=lambda val: self.font_label.configure(text=f"{int(float(val))}"))
        
        # === ACTION BUTTONS ===
        button_frame = ctk.CTkFrame(main_container)
        button_frame.pack(pady=15)
        
        self.generate_btn = ctk.CTkButton(
            button_frame,
            text="🔲 Generate Barcode",
            command=self.generate_barcode,
            width=200,
            height=55,
            font=("Arial", 16, "bold"),
            corner_radius=12
        )
        self.generate_btn.pack(side="left", padx=10)
        
        self.save_btn = ctk.CTkButton(
            button_frame,
            text="💾 Save Barcode",
            command=self.save_barcode,
            width=160,
            height=55,
            font=("Arial", 15),
            corner_radius=12,
            state="disabled"
        )
        self.save_btn.pack(side="left", padx=10)
        
        self.clear_btn = ctk.CTkButton(
            button_frame,
            text="🗑️ Clear",
            command=self.clear_generate,
            width=140,
            height=55,
            font=("Arial", 15),
            corner_radius=12,
            fg_color="#B22222",
            hover_color="#8B0000"
        )
        self.clear_btn.pack(side="left", padx=10)
        
        # === DISPLAY FRAME ===
        display_container = ctk.CTkFrame(main_container, height=300)
        display_container.pack(pady=10, fill="x")
        display_container.pack_propagate(False)
        
        self.display_frame = ctk.CTkFrame(display_container)
        self.display_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.barcode_display = ctk.CTkLabel(
            self.display_frame,
            text="📊 Barcode will appear here\n\n(Keep aspect ratio: 3:1)",
            font=("Arial", 18),
            justify="center"
        )
        self.barcode_display.pack(expand=True, fill="both")
        
        # === STATUS ===
        self.generate_status = ctk.CTkLabel(
            main_container,
            text="✅ Ready to generate",
            font=("Arial", 13)
        )
        self.generate_status.pack(pady=5)
    
    def setup_verify_tab(self):
        """Setup the verify barcode tab"""
        verify_tab = self.tabview.tab("✅ Verify")
        
        # Main container
        main_container = ctk.CTkScrollableFrame(verify_tab)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_frame = ctk.CTkFrame(main_container)
        title_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            title_frame,
            text="✅ Verify Barcode",
            font=("Arial", 28, "bold")
        ).pack(pady=5)
        
        ctk.CTkLabel(
            title_frame,
            text="Check if a barcode is valid or scan a barcode image",
            font=("Arial", 14)
        ).pack()
        
        # === MANUAL VERIFICATION ===
        manual_frame = ctk.CTkFrame(main_container)
        manual_frame.pack(pady=10, fill="x")
        
        ctk.CTkLabel(
            manual_frame,
            text="🔍 Manual Verification:",
            font=("Arial", 16, "bold")
        ).pack(pady=5, anchor="w", padx=10)
        
        ctk.CTkLabel(
            manual_frame,
            text="Enter the barcode data to verify:",
            font=("Arial", 13)
        ).pack(anchor="w", padx=10)
        
        # Entry with type selector
        entry_frame = ctk.CTkFrame(manual_frame)
        entry_frame.pack(pady=5, padx=10, fill="x")
        
        self.verify_entry = ctk.CTkEntry(
            entry_frame,
            height=45,
            placeholder_text="Enter barcode digits to verify...",
            font=("Arial", 15)
        )
        self.verify_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.verify_type = ctk.CTkComboBox(
            entry_frame,
            values=["Auto Detect", "CODE128", "EAN-13", "EAN-8", "UPC-A", "Code39", "ISBN-10"],
            width=150,
            height=40,
            font=("Arial", 13)
        )
        self.verify_type.pack(side="right")
        self.verify_type.set("Auto Detect")
        
        # Action buttons
        verify_btn_frame = ctk.CTkFrame(manual_frame)
        verify_btn_frame.pack(pady=10)
        
        self.verify_btn = ctk.CTkButton(
            verify_btn_frame,
            text="✅ Verify Barcode",
            command=self.verify_barcode_from_input,
            width=200,
            height=45,
            font=("Arial", 15, "bold"),
            corner_radius=10
        )
        self.verify_btn.pack(side="left", padx=8)
        
        self.scan_btn = ctk.CTkButton(
            verify_btn_frame,
            text="📷 Scan Image",
            command=self.scan_barcode_image,
            width=170,
            height=45,
            font=("Arial", 14),
            corner_radius=10,
            fg_color="#2E8B57",
            hover_color="#1C6B3B"
        )
        self.scan_btn.pack(side="left", padx=8)
        
        # Quick test buttons
        test_frame = ctk.CTkFrame(manual_frame)
        test_frame.pack(pady=10)
        
        ctk.CTkLabel(
            test_frame,
            text="⚡ Quick Test:",
            font=("Arial", 13, "bold")
        ).pack(side="left", padx=10)
        
        test_values = [
            ("EAN-13", "5901234123457"),
            ("UPC-A", "036000291452"),
            ("CODE128", "Hello123"),
            ("EAN-8", "96385074")
        ]
        
        for label, value in test_values:
            ctk.CTkButton(
                test_frame,
                text=label,
                command=lambda v=value: self.set_verify_data(v),
                width=90,
                height=32,
                font=("Arial", 12),
                fg_color="#3B8ED0",
                hover_color="#2B6EA0"
            ).pack(side="left", padx=5)
        
        # === VERIFICATION RESULTS ===
        results_frame = ctk.CTkFrame(main_container)
        results_frame.pack(pady=10, fill="both", expand=True)
        
        # Result header
        result_header = ctk.CTkFrame(results_frame)
        result_header.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            result_header,
            text="📊 Verification Results:",
            font=("Arial", 16, "bold")
        ).pack(side="left", padx=15)
        
        self.verify_status = ctk.CTkLabel(
            result_header,
            text="⏳ Waiting for input...",
            font=("Arial", 15)
        )
        self.verify_status.pack(side="right", padx=15)
        
        # Details grid
        details_frame = ctk.CTkFrame(results_frame)
        details_frame.pack(fill="x", pady=10, padx=15)
        
        details = [
            ("📝 Data:", "v_data"),
            ("📊 Type:", "v_type"),
            ("📏 Length:", "v_length"),
            ("🔢 Checksum:", "v_checksum"),
            ("✅ Status:", "v_valid")
        ]
        
        self.verify_details = {}
        for label, key in details:
            row_frame = ctk.CTkFrame(details_frame)
            row_frame.pack(fill="x", pady=5)
            
            ctk.CTkLabel(
                row_frame,
                text=label,
                font=("Arial", 14, "bold"),
                width=140
            ).pack(side="left", padx=15)
            
            self.verify_details[key] = ctk.CTkLabel(
                row_frame,
                text="—",
                font=("Arial", 14),
                width=300
            )
            self.verify_details[key].pack(side="left", padx=15)
        
        # Verification history
        history_frame = ctk.CTkFrame(results_frame)
        history_frame.pack(fill="both", expand=True, pady=10, padx=15)
        
        ctk.CTkLabel(
            history_frame,
            text="📜 Verification History:",
            font=("Arial", 15, "bold")
        ).pack(pady=5, anchor="w")
        
        self.verify_history_text = ctk.CTkTextbox(
            history_frame,
            height=150,
            font=("Arial", 13)
        )
        self.verify_history_text.pack(fill="both", expand=True, padx=5, pady=5)
    
    def setup_history_tab(self):
        """Setup the history tab"""
        history_tab = self.tabview.tab("📋 History")
        
        main_container = ctk.CTkScrollableFrame(history_tab)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_frame = ctk.CTkFrame(main_container)
        title_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            title_frame,
            text="📋 Generation History",
            font=("Arial", 28, "bold")
        ).pack(pady=5)
        
        ctk.CTkLabel(
            title_frame,
            text="Your recently generated barcodes",
            font=("Arial", 14)
        ).pack()
        
        # Statistics
        stats_frame = ctk.CTkFrame(main_container)
        stats_frame.pack(fill="x", pady=10)
        
        self.total_count = ctk.CTkLabel(
            stats_frame,
            text="📊 Total Generated: 0",
            font=("Arial", 14, "bold")
        )
        self.total_count.pack(side="left", padx=20)
        
        self.valid_count = ctk.CTkLabel(
            stats_frame,
            text="✅ Valid: 0",
            font=("Arial", 14, "bold"),
            text_color="#00FF00"
        )
        self.valid_count.pack(side="left", padx=20)
        
        self.invalid_count = ctk.CTkLabel(
            stats_frame,
            text="❌ Invalid: 0",
            font=("Arial", 14, "bold"),
            text_color="#FF4444"
        )
        self.invalid_count.pack(side="left", padx=20)
        
        # History list
        self.history_frame = ctk.CTkFrame(main_container)
        self.history_frame.pack(fill="both", expand=True, pady=10)
        
        self.history_text = ctk.CTkTextbox(
            self.history_frame,
            font=("Arial", 14),
            wrap="word"
        )
        self.history_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Buttons
        btn_frame = ctk.CTkFrame(main_container)
        btn_frame.pack(pady=15)
        
        ctk.CTkButton(
            btn_frame,
            text="🗑️ Clear History",
            command=self.clear_history,
            width=170,
            height=45,
            font=("Arial", 14),
            fg_color="#B22222",
            hover_color="#8B0000",
            corner_radius=10
        ).pack(side="left", padx=8)
        
        ctk.CTkButton(
            btn_frame,
            text="📤 Export History",
            command=self.export_history,
            width=170,
            height=45,
            font=("Arial", 14),
            fg_color="#2E8B57",
            hover_color="#1C6B3B",
            corner_radius=10
        ).pack(side="left", padx=8)
    
    def setup_settings_tab(self):
        """Setup settings tab"""
        settings_tab = self.tabview.tab("⚙️ Settings")
        
        main_container = ctk.CTkScrollableFrame(settings_tab)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_frame = ctk.CTkFrame(main_container)
        title_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            title_frame,
            text="⚙️ Settings",
            font=("Arial", 28, "bold")
        ).pack(pady=5)
        
        ctk.CTkLabel(
            title_frame,
            text="Application preferences and settings",
            font=("Arial", 14)
        ).pack()
        
        # Appearance settings
        appearance_frame = ctk.CTkFrame(main_container)
        appearance_frame.pack(pady=10, fill="x")
        
        ctk.CTkLabel(
            appearance_frame,
            text="🎨 Appearance:",
            font=("Arial", 16, "bold")
        ).pack(pady=5, anchor="w", padx=10)
        
        # Theme selector
        theme_frame = ctk.CTkFrame(appearance_frame)
        theme_frame.pack(pady=5, padx=10, fill="x")
        
        ctk.CTkLabel(
            theme_frame,
            text="Theme:",
            font=("Arial", 14)
        ).pack(side="left", padx=10)
        
        self.theme_var = ctk.StringVar(value="dark")
        themes = ["dark", "light"]
        
        for theme in themes:
            ctk.CTkRadioButton(
                theme_frame,
                text=theme.capitalize(),
                variable=self.theme_var,
                value=theme,
                command=lambda t=theme: ctk.set_appearance_mode(t),
                font=("Arial", 13)
            ).pack(side="left", padx=10)
        
        # Default settings
        default_frame = ctk.CTkFrame(main_container)
        default_frame.pack(pady=10, fill="x")
        
        ctk.CTkLabel(
            default_frame,
            text="🔧 Default Settings:",
            font=("Arial", 16, "bold")
        ).pack(pady=5, anchor="w", padx=10)
        
        # Default barcode type
        default_type_frame = ctk.CTkFrame(default_frame)
        default_type_frame.pack(pady=5, padx=10, fill="x")
        
        ctk.CTkLabel(
            default_type_frame,
            text="Default Barcode Type:",
            font=("Arial", 14)
        ).pack(side="left", padx=10)
        
        self.default_type = ctk.CTkComboBox(
            default_type_frame,
            values=["CODE128", "EAN-13", "EAN-8", "UPC-A", "Code39", "ISBN-10"],
            width=150,
            height=35,
            font=("Arial", 13)
        )
        self.default_type.pack(side="left", padx=10)
        self.default_type.set("CODE128")
        
        ctk.CTkButton(
            default_type_frame,
            text="Apply Default",
            command=self.apply_defaults,
            width=120,
            height=35,
            font=("Arial", 13),
            fg_color="#2E8B57",
            hover_color="#1C6B3B"
        ).pack(side="left", padx=10)
        
        # Info
        info_frame = ctk.CTkFrame(main_container)
        info_frame.pack(pady=10, fill="x")
        
        ctk.CTkLabel(
            info_frame,
            text="ℹ️ About:",
            font=("Arial", 16, "bold")
        ).pack(pady=5, anchor="w", padx=10)
        
        ctk.CTkLabel(
            info_frame,
            text="Barcode Generator & Checker Pro v2.0\n"
                 "Created with CustomTkinter and python-barcode\n"
                 "© 2024 All Rights Reserved",
            font=("Arial", 13),
            justify="left"
        ).pack(pady=10, padx=10)
    
    def set_verify_data(self, value):
        """Set verification entry with test data"""
        self.verify_entry.delete(0, 'end')
        self.verify_entry.insert(0, value)
        # Auto-verify after setting
        self.verify_barcode_from_input()
    
    def apply_defaults(self):
        """Apply default settings"""
        default_type = self.default_type.get()
        self.barcode_type.set(default_type)
        messagebox.showinfo("Settings Applied", f"Default barcode type set to: {default_type}")
    
    def generate_barcode(self):
        """Generate barcode from input"""
        data = self.link_entry.get().strip()
        
        if not data:
            messagebox.showwarning("Input Required", "Please enter data to generate barcode.")
            self.generate_status.configure(text="❌ Error: No input provided", text_color="#FF4444")
            return
        
        barcode_type = self.barcode_type.get()
        module_width = float(self.size_slider.get())
        module_height = float(self.height_slider.get())
        font_size = int(float(self.font_slider.get()))
        
        # Validate
        if not self.validate_input(data, barcode_type):
            return
        
        try:
            self.generate_status.configure(text="⏳ Generating barcode...", text_color="#FFD700")
            self.window.update()
            
            # Map barcode type
            type_map = {
                "CODE128": "code128",
                "EAN-13": "ean13",
                "EAN-8": "ean8",
                "UPC-A": "upca",
                "Code39": "code39",
                "ISBN-10": "isbn10"
            }
            
            barcode_format = type_map.get(barcode_type, "code128")
            barcode_class = barcode.get_barcode_class(barcode_format)
            
            # Writer options
            writer_options = {
                'module_width': module_width * 0.4,
                'module_height': module_height,
                'font_size': font_size,
                'text_distance': 6.0,
                'background': 'white',
                'foreground': 'black',
                'center_text': True,
                'write_text': True
            }
            
            barcode_obj = barcode_class(data, writer=ImageWriter())
            barcode_obj.writer.set_options(writer_options)
            
            # Save
            temp_path = f"temp_barcode_{barcode_type.lower()}"
            filename = barcode_obj.save(temp_path)
            
            self.current_barcode_path = filename
            self.current_data = data
            
            # Display
            self.display_barcode(filename)
            
            # Enable save button
            self.save_btn.configure(state="normal")
            
            # Add to history
            is_valid = self.verify_barcode(data, barcode_type)
            self.add_to_history(data, barcode_type, "Generated", is_valid)
            
            # Update status
            if is_valid:
                self.generate_status.configure(text="✅ Barcode generated and verified successfully!", text_color="#00FF00")
            else:
                self.generate_status.configure(text="⚠️ Barcode generated but verification failed!", text_color="#FFD700")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate barcode: {str(e)}")
            self.generate_status.configure(text="❌ Error generating barcode", text_color="#FF4444")
    
    def display_barcode(self, image_path):
        """Display the generated barcode with proper aspect ratio"""
        try:
            # Load image
            img = Image.open(image_path)
            
            # Get display frame size
            display_width = self.display_frame.winfo_width() - 20
            display_height = self.display_frame.winfo_height() - 20
            
            if display_width <= 0:
                display_width = 600
            if display_height <= 0:
                display_height = 250
            
            # Maintain aspect ratio
            img_width, img_height = img.size
            aspect_ratio = img_width / img_height
            
            # Calculate new dimensions
            target_width = min(display_width, int(display_height * aspect_ratio))
            target_height = min(display_height, int(display_width / aspect_ratio))
            
            # Ensure minimum size
            target_width = max(target_width, 200)
            target_height = max(target_height, 80)
            
            # Resize
            img_resized = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(img_resized)
            
            # Clear previous
            for widget in self.display_frame.winfo_children():
                widget.destroy()
            
            # Display new image
            image_label = ctk.CTkLabel(
                self.display_frame,
                image=photo,
                text=""
            )
            image_label.image = photo
            image_label.pack(expand=True, fill="both", padx=10, pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display barcode: {str(e)}")
    
    def verify_barcode_from_input(self):
        """Verify barcode from the verify tab input"""
        data = self.verify_entry.get().strip()
        
        if not data:
            self.verify_status.configure(text="⏳ Waiting for input...", text_color="white")
            for key in self.verify_details:
                self.verify_details[key].configure(text="—")
            return
        
        # Get verification type
        verify_type = self.verify_type.get()
        
        # Auto-detect or use specified type
        if verify_type == "Auto Detect":
            barcode_type = self.detect_barcode_type(data)
        else:
            barcode_type = verify_type
        
        if not barcode_type:
            self.verify_status.configure(
                text="❌ Unknown barcode type",
                text_color="#FF4444"
            )
            self.verify_details["v_valid"].configure(
                text="❌ Unknown",
                text_color="#FF4444"
            )
            return
        
        # Verify
        is_valid = self.verify_barcode(data, barcode_type)
        
        # Update verification details
        self.verify_details["v_data"].configure(text=data[:60] + ('...' if len(data) > 60 else ''))
        self.verify_details["v_type"].configure(text=barcode_type)
        self.verify_details["v_length"].configure(text=str(len(data)))
        
        # Calculate checksum
        checksum = self.calculate_checksum(data, barcode_type)
        self.verify_details["v_checksum"].configure(text=checksum if checksum else "N/A")
        
        # Update status
        if is_valid:
            self.verify_status.configure(
                text="✅ Valid Barcode ✓",
                text_color="#00FF00"
            )
            self.verify_details["v_valid"].configure(
                text="✅ Valid",
                text_color="#00FF00"
            )
            self.add_verify_history(f"✅ Valid: {data[:30]}{'...' if len(data) > 30 else ''} ({barcode_type})")
        else:
            self.verify_status.configure(
                text="❌ Invalid Barcode ✗",
                text_color="#FF4444"
            )
            self.verify_details["v_valid"].configure(
                text="❌ Invalid",
                text_color="#FF4444"
            )
            self.add_verify_history(f"❌ Invalid: {data[:30]}{'...' if len(data) > 30 else ''} ({barcode_type})")
    
    def verify_barcode(self, data, barcode_type):
        """Verify barcode validity"""
        try:
            type_map = {
                "CODE128": "code128",
                "EAN-13": "ean13",
                "EAN-8": "ean8",
                "UPC-A": "upca",
                "Code39": "code39",
                "ISBN-10": "isbn10"
            }
            
            barcode_format = type_map.get(barcode_type, "code128")
            barcode_class = barcode.get_barcode_class(barcode_format)
            
            # Try to create barcode object
            barcode_obj = barcode_class(data)
            return True
            
        except Exception as e:
            return False
    
    def detect_barcode_type(self, data):
        """Detect barcode type from data"""
        if data.isdigit():
            length = len(data)
            if length == 13:
                return "EAN-13"
            elif length == 8:
                return "EAN-8"
            elif length == 12:
                return "UPC-A"
            elif length == 10:
                return "ISBN-10"
        
        # Try each type
        types = ["CODE128", "Code39", "EAN-13", "EAN-8", "UPC-A", "ISBN-10"]
        for barcode_type in types:
            try:
                if self.verify_barcode(data, barcode_type):
                    return barcode_type
            except:
                continue
        
        return None
    
    def calculate_checksum(self, data, barcode_type):
        """Calculate checksum for different barcode types"""
        if barcode_type in ["EAN-13", "EAN-8", "UPC-A"]:
            if not data.isdigit():
                return "N/A"
            
            digits = [int(d) for d in data]
            if barcode_type in ["EAN-13", "UPC-A"]:
                weights = [1, 3] * 6
                if barcode_type == "EAN-13":
                    weights = [1, 3] * 6 + [1]
                sum_weights = sum(d * w for d, w in zip(digits, weights))
                checksum = (10 - (sum_weights % 10)) % 10
                return str(checksum)
            
            elif barcode_type == "EAN-8":
                weights = [3, 1] * 4
                sum_weights = sum(d * w for d, w in zip(digits, weights))
                checksum = (10 - (sum_weights % 10)) % 10
                return str(checksum)
        
        return "N/A"
    
    def validate_input(self, data, barcode_type):
        """Validate input based on barcode type"""
        if barcode_type in ["EAN-13", "EAN-8", "UPC-A"]:
            if not data.isdigit():
                messagebox.showwarning("Invalid Input", 
                    f"{barcode_type} requires numeric data only.")
                return False
            
            length_map = {"EAN-13": 13, "EAN-8": 8, "UPC-A": 12}
            required_length = length_map.get(barcode_type)
            
            if len(data) != required_length:
                messagebox.showwarning("Invalid Length", 
                    f"{barcode_type} requires exactly {required_length} digits.\nCurrent length: {len(data)}")
                return False
        
        elif barcode_type == "ISBN-10":
            clean_data = data.replace("-", "")
            if not clean_data.isdigit() and len(clean_data) != 10:
                messagebox.showwarning("Invalid ISBN", 
                    "ISBN-10 must be 10 digits (hyphens allowed).")
                return False
        
        return True
    
    def scan_barcode_image(self):
        """Scan a barcode image file"""
        file_path = filedialog.askopenfilename(
            title="Select Barcode Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            # Try to decode with pyzbar if available
            try:
                from pyzbar import pyzbar
                from PIL import Image
                
                # Decode barcode
                img_pil = Image.open(file_path)
                decoded = pyzbar.decode(img_pil)
                
                if decoded:
                    for barcode_obj in decoded:
                        data = barcode_obj.data.decode('utf-8')
                        barcode_type = barcode_obj.type
                        self.verify_entry.delete(0, 'end')
                        self.verify_entry.insert(0, data)
                        self.verify_type.set(barcode_type)
                        self.verify_barcode_from_input()
                        self.add_verify_history(f"📷 Scanned: {data[:30]}{'...' if len(data) > 30 else ''} ({barcode_type})")
                        return
                else:
                    self.verify_status.configure(
                        text="❌ No barcode found in image",
                        text_color="#FF4444"
                    )
                    self.add_verify_history("❌ No barcode found in image")
                    
            except ImportError:
                # pyzbar not installed
                self.verify_status.configure(
                    text="📷 Image loaded - Install pyzbar for decoding",
                    text_color="#FFD700"
                )
                self.add_verify_history("ℹ️ Install pyzbar: pip install pyzbar")
                self.verify_details["v_data"].configure(text=f"Image: {os.path.basename(file_path)}")
                self.verify_details["v_type"].configure(text="Image Scan")
                self.verify_details["v_valid"].configure(text="📷 Ready", text_color="#FFD700")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
    
    def add_to_history(self, data, barcode_type, action, is_valid=None):
        """Add entry to history"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if is_valid is True:
            status = "✅ Valid"
        elif is_valid is False:
            status = "❌ Invalid"
        else:
            status = "—"
        
        entry = f"[{timestamp}] {status} {action}: {data[:40]}{'...' if len(data) > 40 else ''} ({barcode_type})\n"
        
        self.history.append(entry)
        self.history_text.insert("end", entry)
        self.history_text.see("end")
        
        # Update statistics
        self.update_statistics()
        
        # Also add to verification history
        self.add_verify_history(f"{action}: {data[:30]}{'...' if len(data) > 30 else ''} ({barcode_type})")
    
    def add_verify_history(self, text):
        """Add entry to verification history"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] {text}\n"
        
        self.verify_history_text.insert("end", entry)
        self.verify_history_text.see("end")
        self.verification_history.append(entry)
    
    def update_statistics(self):
        """Update statistics in history tab"""
        total = len(self.history)
        valid = sum(1 for h in self.history if "✅ Valid" in h)
        invalid = sum(1 for h in self.history if "❌ Invalid" in h)
        
        self.total_count.configure(text=f"📊 Total Generated: {total}")
        self.valid_count.configure(text=f"✅ Valid: {valid}")
        self.invalid_count.configure(text=f"❌ Invalid: {invalid}")
    
    def clear_history(self):
        """Clear history"""
        if messagebox.askyesno("Clear History", "Are you sure you want to clear all history?"):
            self.history.clear()
            self.verification_history.clear()
            self.history_text.delete("1.0", "end")
            self.verify_history_text.delete("1.0", "end")
            self.update_statistics()
    
    def export_history(self):
        """Export history to file"""
        if not self.history:
            messagebox.showwarning("No History", "No history to export.")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Export History"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("BARCODE GENERATOR HISTORY\n")
                    f.write("=" * 50 + "\n\n")
                    f.writelines(self.history)
                messagebox.showinfo("Success", f"✅ History exported successfully!\n📍 {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {str(e)}")
    
    def save_barcode(self):
        """Save barcode to file"""
        if not self.current_barcode_path:
            messagebox.showwarning("No Barcode", "Please generate a barcode first.")
            return
        
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("JPG files", "*.jpg"), ("All files", "*.*")],
                title="Save Barcode",
                initialfile=f"barcode_{self.barcode_type.get()}"
            )
            
            if file_path:
                shutil.copy2(self.current_barcode_path, file_path)
                messagebox.showinfo("Success", f"✅ Barcode saved successfully!\n📍 {file_path}")
                self.generate_status.configure(text=f"💾 Saved to: {os.path.basename(file_path)}", text_color="#00FF00")
                
                if messagebox.askyesno("Open Location", "Open file location?"):
                    webbrowser.open(os.path.dirname(os.path.abspath(file_path)))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {str(e)}")
    
    def clear_generate(self):
        """Clear generate tab"""
        self.link_entry.delete(0, 'end')
        
        # Clear display
        for widget in self.display_frame.winfo_children():
            widget.destroy()
        
        self.barcode_display = ctk.CTkLabel(
            self.display_frame,
            text="📊 Barcode will appear here\n\n(Keep aspect ratio: 3:1)",
            font=("Arial", 18),
            justify="center"
        )
        self.barcode_display.pack(expand=True, fill="both")
        
        self.save_btn.configure(state="disabled")
        self.generate_status.configure(text="✅ Ready to generate", text_color="#00FF00")
        
        # Clean up
        if self.current_barcode_path and os.path.exists(self.current_barcode_path):
            try:
                os.remove(self.current_barcode_path)
            except:
                pass
        
        self.current_barcode_path = None
        self.current_data = None
    
    def show_installation_required(self):
        """Show installation message"""
        message = """⚠️ Required packages not installed!

Please install:
pip install python-barcode pillow customtkinter

Then restart the application."""
        
        label = ctk.CTkLabel(
            self.window,
            text=message,
            font=("Arial", 18),
            text_color="#FF4444"
        )
        label.pack(expand=True, fill="both", padx=50, pady=50)
        
        install_btn = ctk.CTkButton(
            self.window,
            text="📦 Install Packages",
            command=self.install_packages,
            width=220,
            height=55,
            font=("Arial", 15, "bold"),
            corner_radius=12
        )
        install_btn.pack(pady=20)
    
    def install_packages(self):
        """Install required packages"""
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "python-barcode", "pillow", "customtkinter"])
            messagebox.showinfo("Success", "Packages installed successfully!\nPlease restart the application.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to install packages: {str(e)}")
    
    def run(self):
        """Run the application"""
        self.window.mainloop()

# Main execution
if __name__ == "__main__":
    app = BarcodeGeneratorApp()
    app.run()