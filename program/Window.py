from PyQt6.QtWidgets import (QApplication, QWidget, QMainWindow, QVBoxLayout, QHBoxLayout,
                             QTabWidget, QLabel, QListWidget, QListWidgetItem, QScrollArea,
                             QPushButton, QDialog, QMessageBox)
from PyQt6.QtCore import Qt
from SystemCanvas import SystemCanvas
import GlobalVariableAccess as gva
import requests as rq


class MainWindow(QMainWindow):
    """
    Main application window with a tabbed interface.
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SpaceTrader API GUI")
        self.resize(1200, 800)
        
        # Dictionary to store all tabs: {"tab_name": {"widget": QWidget, "layout": QVBoxLayout}}
        self.tabs_dict = {}
        
        # Create central widget and main layout
        self.central_widget = QWidget()
        self.main_layout = QVBoxLayout()
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        
        self.central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.central_widget)
        
        # Initialize tabs
        self._setup_ships_tab()
        self._setup_canvas_tab()
    
    def _setup_ships_tab(self):
        """Set up the Ships tab with ship list and details."""
        # Create tab widget and layout
        tab_widget = QWidget()
        main_layout = QVBoxLayout()
        tab_widget.setLayout(main_layout)
        
        # Store reference
        self.tabs_dict["Ships"] = {
            "widget": tab_widget,
            "layout": main_layout
        }
        
        # TOP: Horizontal layout for details and list
        content_layout = QHBoxLayout()
        
        # LEFT SIDE: Ship Details (scrollable)
        details_scroll = QScrollArea()
        details_scroll.setWidgetResizable(True)
        details_widget = QWidget()
        details_layout = QVBoxLayout()
        details_widget.setLayout(details_layout)
        details_scroll.setWidget(details_widget)
        
        # Ship details labels
        self.ship_name_label = QLabel("No ship selected")
        self.ship_name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        self.ship_location_label = QLabel("Location: N/A")
        self.ship_status_label = QLabel("Status: N/A")
        self.ship_cargo_label = QLabel("Cargo: N/A")
        
        details_layout.addWidget(QLabel("Ship Details:"))
        details_layout.addWidget(self.ship_name_label)
        details_layout.addWidget(self.ship_location_label)
        details_layout.addWidget(self.ship_status_label)
        details_layout.addWidget(self.ship_cargo_label)
        
        # PLANET DETAILS SECTION
        details_layout.addWidget(QLabel(""))  # Spacer
        details_layout.addWidget(QLabel("Waypoint Details:"))
        
        self.waypoint_name_label = QLabel("Waypoint: N/A")
        self.waypoint_name_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        self.waypoint_type_label = QLabel("Type: N/A")
        self.waypoint_traits_label = QLabel("Traits: N/A")
        
        details_layout.addWidget(self.waypoint_name_label)
        details_layout.addWidget(self.waypoint_type_label)
        details_layout.addWidget(self.waypoint_traits_label)
        
        # FUNCTIONS WIDGET
        functions_layout = QVBoxLayout()
        functions_layout.addWidget(QLabel("Functions:"))
        
        # Dock/Orbit buttons
        dock_orbit_layout = QHBoxLayout()
        self.dock_button = QPushButton("Dock")
        self.orbit_button = QPushButton("Orbit")
        self.dock_button.clicked.connect(self._on_dock_clicked)
        self.orbit_button.clicked.connect(self._on_orbit_clicked)
        dock_orbit_layout.addWidget(self.dock_button)
        dock_orbit_layout.addWidget(self.orbit_button)
        functions_layout.addLayout(dock_orbit_layout)
        
        # Travel button
        self.travel_button = QPushButton("Travel")
        self.travel_button.clicked.connect(self._on_travel_clicked)
        functions_layout.addWidget(self.travel_button)
        
        # Mine button
        self.mine_button = QPushButton("Mine")
        self.mine_button.clicked.connect(self._on_mine_clicked)
        functions_layout.addWidget(self.mine_button)
        
        functions_layout.addStretch()
        details_layout.addLayout(functions_layout)
        
        # RIGHT SIDE: Ship List
        list_container = QWidget()
        list_layout = QVBoxLayout()
        list_container.setLayout(list_layout)
        
        list_layout.addWidget(QLabel("Ships:"))
        
        # Create ship list widget
        self.ship_list = QListWidget()
        self.ship_list.itemClicked.connect(self._on_ship_selected)
        list_layout.addWidget(self.ship_list)
        
        # Load ships from global variable
        self._load_ships()
        self.ship_list.setCurrentRow(0)
        self._on_ship_selected(self.ship_list.item(0))
        
        # Add to content layout (details on left, list on right)
        content_layout.addWidget(details_scroll, 2)
        content_layout.addWidget(list_container, 1)
        
        # BOTTOM: Update button (bottom right)
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        self.update_info_button = QPushButton("Update Information")
        self.update_info_button.clicked.connect(self._refresh_ship_data)
        bottom_layout.addWidget(self.update_info_button)
        
        # Add content and bottom to main layout
        main_layout.addLayout(content_layout, 1)
        main_layout.addLayout(bottom_layout)
        
        # Add tab to tab widget
        self.tab_widget.addTab(tab_widget, "Ships")
    
    def _load_ships(self):
        """Load ships from gva.ship_data and populate the list."""
        self.ship_list.clear()
        self.ships_data = {}
        
        # Get ships data from global variable (assuming it's a list or dict)
        for ship in gva.ships_data:
            ship_name = ship['symbol']
            self.ships_data[ship_name] = ship
            self.ship_list.addItem(ship_name)

    def _on_ship_selected(self, item):
        """Update details when a ship is selected."""
        ship_name = item.text()
        ship_data = self.ships_data.get(ship_name, {})
        
        # Update labels
        self.ship_name_label.setText(f"Ship: {ship_data.get('symbol', 'N/A')}")
        
        # Location
        nav = ship_data.get('nav', {})
        location = nav.get('waypointSymbol', 'N/A')
        self.ship_location_label.setText(f"Location: {location}")
        
        # Status with ETC if in transit
        status = nav.get('status', 'N/A')
        status_text = f"Status: {status}"
        
        # Add arrival time if ship is in transit
        if status == 'IN_TRANSIT':
            route = nav.get('route', {})
            arrival = route.get('arrival', None)
            if arrival:
                status_text += f" (ETA: {arrival})"
        
        self.ship_status_label.setText(status_text)
        
        # Cargo
        cargo = ship_data.get('cargo', {})
        cargo_items = cargo.get('inventory', [])
        cargo_str = f"Cargo: {len(cargo_items)} items"
        if cargo_items:
            cargo_details = ", ".join([f"{item.get('symbol', 'Unknown')} x{item.get('units', 0)}" for item in cargo_items])
            cargo_str += f"\n{cargo_details}"
        self.ship_cargo_label.setText(cargo_str)
        
        # Load waypoint details
        self._load_waypoint_details(location)
    
    def _setup_canvas_tab(self):
        """Set up the Canvas tab with SystemCanvas."""
        # Create tab widget and layout
        tab_widget = QWidget()
        tab_layout = QVBoxLayout()
        tab_widget.setLayout(tab_layout)
        
        # Store reference
        self.tabs_dict["Canvas"] = {
            "widget": tab_widget,
            "layout": tab_layout
        }
        
        # Create and add SystemCanvas
        system_canvas = SystemCanvas(width=800, height=600)
        if hasattr(gva, 'system_waypoints'):
            system_canvas.set_points(gva.system_waypoints)
        tab_layout.addWidget(system_canvas)
        
        # Add tab to tab widget
        self.tab_widget.addTab(tab_widget, "Canvas")
    
    def _load_waypoint_details(self, waypoint_symbol):
        """Load and display waypoint details."""
        if not waypoint_symbol or waypoint_symbol == 'N/A':
            self.waypoint_name_label.setText("Waypoint: N/A")
            self.waypoint_type_label.setText("Type: N/A")
            self.waypoint_traits_label.setText("Traits: N/A")
            return
        
        try:
            # Try to get waypoint from gva.system_waypoints
            waypoint_data = None
            if hasattr(gva, 'system_waypoints') and waypoint_symbol in gva.system_waypoints:
                waypoint_data = gva.system_waypoints[waypoint_symbol]
            else:
                # Fetch from API if not in cache
                if hasattr(gva, 'current_auth_token') and hasattr(gva, 'system'):
                    headers = {"Authorization": f"Bearer {gva.current_auth_token}"}
                    url = f"https://api.spacetraders.io/v2/systems/{gva.system}/waypoints/{waypoint_symbol}"
                    response = rq.get(url, headers=headers)
                    
                    if response.status_code == 200:
                        waypoint_data = response.json().get('data', {})
            
            if waypoint_data:
                # Display waypoint details
                self.waypoint_name_label.setText(f"Waypoint: {waypoint_data.get('symbol', 'N/A')}")
                self.waypoint_type_label.setText(f"Type: {waypoint_data.get('type', 'N/A')}")
                
                # Display traits
                traits = waypoint_data.get('traits', [])
                traits_str = ", ".join([t.get('symbol', '') for t in traits]) if traits else "None"
                self.waypoint_traits_label.setText(f"Traits: {traits_str}")
            else:
                self.waypoint_name_label.setText(f"Waypoint: {waypoint_symbol}")
                self.waypoint_type_label.setText("Type: N/A")
                self.waypoint_traits_label.setText("Traits: N/A")
        except Exception as e:
            print(f"Error loading waypoint details: {str(e)}")
            self.waypoint_name_label.setText(f"Waypoint: {waypoint_symbol}")
            self.waypoint_type_label.setText("Type: Error")
            self.waypoint_traits_label.setText("Traits: Error")
    
    # ============== Ship Action Methods ==============
    def _get_current_ship(self):
        """Get the currently selected ship data."""
        if not hasattr(self, 'ship_list') or self.ship_list.currentItem() is None:
            return None
        ship_name = self.ship_list.currentItem().text()
        return self.ships_data.get(ship_name, {})
    
    def _on_dock_clicked(self):
        """Handle dock button click."""
        ship = self._get_current_ship()
        if not ship:
            QMessageBox.warning(self, "Error", "No ship selected")
            return
        
        ship_symbol = ship.get('symbol', '')
        try:
            # Make API request to dock the ship
            url = f"https://api.spacetraders.io/v2/my/ships/{ship_symbol}/dock"
            headers = {"Authorization": f"Bearer {gva.current_auth_token}"}
            response = rq.post(url, headers=headers)
            
            if response.status_code in [200, 201]:
                QMessageBox.information(self, "Success", f"{ship_symbol} docked successfully")
                # Refresh ship data
                self._refresh_ship_data()
            else:
                QMessageBox.warning(self, "Error", f"Failed to dock: {response.json().get('error', 'Unknown error')}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error docking ship: {str(e)}")
    
    def _on_orbit_clicked(self):
        """Handle orbit button click."""
        ship = self._get_current_ship()
        if not ship:
            QMessageBox.warning(self, "Error", "No ship selected")
            return
        
        ship_symbol = ship.get('symbol', '')
        try:
            # Make API request to orbit the ship
            url = f"https://api.spacetraders.io/v2/my/ships/{ship_symbol}/orbit"
            headers = {"Authorization": f"Bearer {gva.current_auth_token}"}
            response = rq.post(url, headers=headers)
            
            if response.status_code in [200, 201]:
                QMessageBox.information(self, "Success", f"{ship_symbol} is now in orbit")
                # Refresh ship data
                self._refresh_ship_data()
            else:
                QMessageBox.warning(self, "Error", f"Failed to orbit: {response.json().get('error', 'Unknown error')}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error orbiting ship: {str(e)}")
    
    def _on_travel_clicked(self):
        """Handle travel button click - shows waypoint selection dialog."""
        ship = self._get_current_ship()
        if not ship:
            QMessageBox.warning(self, "Error", "No ship selected")
            return
        
        ship_symbol = ship.get('symbol', '')
        current_location = ship.get('nav', {}).get('waypointSymbol', 'Unknown')
        ship_status = ship.get('nav', {}).get('status', '')
        
        # If not in orbit, first orbit the ship
        if ship_status != 'IN_ORBIT':
            try:
                url = f"https://api.spacetraders.io/v2/my/ships/{ship_symbol}/orbit"
                headers = {"Authorization": f"Bearer {gva.current_auth_token}"}
                response = rq.post(url, headers=headers)
                
                if response.status_code not in [200, 201]:
                    QMessageBox.warning(self, "Error", f"Failed to put ship in orbit: {response.json().get('error', 'Unknown error')}")
                    return
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error orbiting ship: {str(e)}")
                return
        
        # Show travel dialog with waypoints
        dialog = WaypointSelectionDialog(current_location, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            target_waypoint = dialog.selected_waypoint
            self._navigate_ship(ship_symbol, target_waypoint)
    
    def _navigate_ship(self, ship_symbol, target_waypoint):
        """Navigate ship to target waypoint."""
        try:
            url = f"https://api.spacetraders.io/v2/my/ships/{ship_symbol}/navigate"
            headers = {"Authorization": f"Bearer {gva.current_auth_token}"}
            data = {"waypointSymbol": target_waypoint}
            response = rq.post(url, json=data, headers=headers)
            
            if response.status_code in [200, 201]:
                response_data = response.json().get('data', {})
                nav = response_data.get('nav', {})
                arrival_time = nav.get('route', {}).get('arrival', 'Unknown')
                
                # Calculate travel time if available
                travel_info = ""
                if arrival_time and arrival_time != 'Unknown':
                    travel_info = f"\nArrival: {arrival_time}"
                
                QMessageBox.information(self, "Success", f"{ship_symbol} is traveling to {target_waypoint}{travel_info}")
                # Refresh ship data
                self._refresh_ship_data()
            else:
                QMessageBox.warning(self, "Error", f"Failed to navigate: {response.json().get('error', 'Unknown error')}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error navigating ship: {str(e)}")
    
    def _on_mine_clicked(self):
        """Handle mine button click - extract resources from waypoint."""
        ship = self._get_current_ship()
        if not ship:
            QMessageBox.warning(self, "Error", "No ship selected")
            return
        
        ship_symbol = ship.get('symbol', '')
        try:
            # Make API request to mine
            url = f"https://api.spacetraders.io/v2/my/ships/{ship_symbol}/extract"
            headers = {"Authorization": f"Bearer {gva.current_auth_token}"}
            response = rq.post(url, headers=headers)
            
            if response.status_code in [200, 201]:
                response_data = response.json().get('data', {})
                yield_data = response_data.get('extraction', {}).get('yield', {})
                symbol = yield_data.get('symbol', 'Unknown')
                units = yield_data.get('units', 0)
                
                # Get cooldown info
                cooldown = response_data.get('cooldown', {})
                cooldown_remaining = cooldown.get('remainingSeconds', 'Unknown')
                
                message = f"Successfully mined!\n\n"
                message += f"Extracted: {units} units of {symbol}\n"
                message += f"Cooldown: {cooldown_remaining}s remaining"
                
                QMessageBox.information(self, "Mining Success", message)
                # Refresh ship data
                self._refresh_ship_data()
            else:
                error_data = response.json()
                error_message = error_data.get('error', {}).get('message', 'Unknown error')
                
                # Check if error is about no resources
                if 'No resources to extract' in error_message or 'no resources' in error_message.lower():
                    QMessageBox.information(self, "Mining Result", "There are no resources to mine at this location.")
                else:
                    QMessageBox.warning(self, "Mining Error", f"Failed to mine: {error_message}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error mining: {str(e)}")
    
    def _refresh_ship_data(self):
        """Refresh ship data from the API."""
        try:
            if hasattr(gva, 'current_auth_token'):
                headers = {"Authorization": f"Bearer {gva.current_auth_token}"}
                response = rq.get("https://api.spacetraders.io/v2/my/ships", headers=headers)
                
                if response.status_code == 200:
                    gva.ships_data = response.json().get('data', [])
                    self._load_ships()
        except Exception as e:
            print(f"Error refreshing ship data: {str(e)}")


class WaypointSelectionDialog(QDialog):
    """Dialog to select a waypoint for travel."""
    
    def __init__(self, current_waypoint, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Destination")
        self.setModal(True)
        self.resize(400, 500)
        self.selected_waypoint = None
        self.current_waypoint = current_waypoint
        
        layout = QVBoxLayout()
        
        # Header
        layout.addWidget(QLabel("Select a waypoint to travel to:"))
        layout.addWidget(QLabel(f"Current location: {current_waypoint}"))
        layout.addWidget(QLabel(""))
        
        # Waypoints list
        self.waypoint_list = QListWidget()
        self._load_waypoints()
        self.waypoint_list.itemClicked.connect(self._on_waypoint_selected)
        layout.addWidget(self.waypoint_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        travel_button = QPushButton("Travel")
        cancel_button = QPushButton("Cancel")
        
        travel_button.clicked.connect(self._on_travel)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(travel_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def _load_waypoints(self):
        """Load and display all waypoints from the current system."""
        self.waypoint_list.clear()
        
        try:
            # Get waypoints from system
            if hasattr(gva, 'system_waypoints') and gva.system_waypoints:
                for waypoint_symbol in sorted(gva.system_waypoints.keys()):
                    display_text = waypoint_symbol
                    
                    # Mark current waypoint
                    if waypoint_symbol == self.current_waypoint:
                        display_text += " (Current Location)"
                    
                    item = QListWidgetItem(display_text)
                    item.setData(Qt.ItemDataRole.UserRole, waypoint_symbol)  # Store symbol as data
                    self.waypoint_list.addItem(item)
            else:
                # Fallback: try to fetch waypoints from API
                if hasattr(gva, 'current_auth_token') and hasattr(gva, 'system'):
                    headers = {"Authorization": f"Bearer {gva.current_auth_token}"}
                    url = f"https://api.spacetraders.io/v2/systems/{gva.system}/waypoints"
                    response = rq.get(url, headers=headers)
                    
                    if response.status_code == 200:
                        waypoints = response.json().get('data', [])
                        for waypoint in sorted(waypoints, key=lambda w: w.get('symbol', '')):
                            waypoint_symbol = waypoint.get('symbol', '')
                            display_text = waypoint_symbol
                            
                            # Mark current waypoint
                            if waypoint_symbol == self.current_waypoint:
                                display_text += " (Current Location)"
                            
                            item = QListWidgetItem(display_text)
                            item.setData(Qt.ItemDataRole.UserRole, waypoint_symbol)
                            self.waypoint_list.addItem(item)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load waypoints: {str(e)}")
    
    def _on_waypoint_selected(self, item):
        """Store selected waypoint."""
        self.selected_waypoint = item.data(Qt.ItemDataRole.UserRole)
    
    def _on_travel(self):
        """Accept the dialog and travel."""
        if self.selected_waypoint is None:
            QMessageBox.warning(self, "Error", "Please select a waypoint")
            return
        self.accept()