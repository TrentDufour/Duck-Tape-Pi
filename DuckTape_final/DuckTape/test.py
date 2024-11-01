import pygame
import sys
import mysql.connector as mariadb

# Database connection setup
class DTdatabase:
    def __init__(self):
        self.mariadb_connection = mariadb.connect(
            user='sqluser',
            password='123',
            database="DuckTape",
            host='localhost'
        )
        self.create_cusor = self.mariadb_connection.cursor()
        self.histdict = {}

    def history(self):
        sql_statement = "SELECT * FROM pics ORDER BY date DESC LIMIT 5;"
        self.create_cusor.execute(sql_statement)
        result = self.create_cusor.fetchall()
        for i in result:
            key = str(i[-1])
            value = 2
            self.histdict[key] = value
        return self.histdict.keys()

    def record(self, date):
        sql_statement = "SELECT * FROM pics WHERE date = %s;"
        self.create_cusor.execute(sql_statement, (date,))
        return self.create_cusor.fetchall()

    def last(self):
        sql_statement = "SELECT * FROM pics ORDER BY date DESC LIMIT 1;"
        self.create_cusor.execute(sql_statement)
        return self.create_cusor.fetchall()

# Initialize Pygame
pygame.init()

# Set up the display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("DuckTape - Wood Duck Monitoring")

# Initialize database
db = DTdatabase()

# Pictures and responses
images = {}
responses = {}

# Load historical data from database
for date in db.history():
    record = db.record(date)
    if record:
        images[date] = record[0][0]  # Assuming the first column is the image path
        responses[date] = record[0][1]  # Assuming the second column is the response

# Colors
BACKGROUND_COLOR = (240, 235, 220)
HEADER_COLOR = (120, 85, 70)
BUTTON_COLOR = (70, 130, 180)
BUTTON_HOVER_COLOR = (100, 149, 237)
TEXT_COLOR = (255, 255, 255)

# Fonts
title_font = pygame.font.Font(None, 48)
button_font = pygame.font.Font(None, 32)

# Button setup
button_history_text = button_font.render("Show History", True, TEXT_COLOR)
button_latest_image_text = button_font.render("Show Latest Image", True, TEXT_COLOR)
button_history_rect = pygame.Rect(100, 550, 200, 50)
button_latest_image_rect = pygame.Rect(500, 550, 210, 50)

# Simulated list of dates
dates = list(images.keys())
date_buttons = [pygame.Rect(300, 150 + i * 60, 200, 40) for i in range(len(dates))]

# Flags for displaying sections
show_history = False
show_latest_image = False
selected_date = None  # To keep track of the selected date

# Title setup
title_text = title_font.render("DuckTape - Wood Duck Monitoring", True, TEXT_COLOR)
title_rect = title_text.get_rect(center=(width // 2, 40))

def draw_button(button_rect, text, color):
    pygame.draw.rect(screen, color, button_rect, border_radius=10)
    screen.blit(text, (button_rect.x + (button_rect.width - text.get_width()) // 2,
                       button_rect.y + (button_rect.height - text.get_height()) // 2))

def draw_home_page():
    screen.fill(BACKGROUND_COLOR)
    pygame.draw.rect(screen, HEADER_COLOR, (0, 0, width, 80))  # Header bar
    screen.blit(title_text, title_rect)  # Title

    # Draw buttons with hover effects
    mouse_pos = pygame.mouse.get_pos()
    if button_history_rect.collidepoint(mouse_pos):
        draw_button(button_history_rect, button_history_text, BUTTON_HOVER_COLOR)
    else:
        draw_button(button_history_rect, button_history_text, BUTTON_COLOR)

    if button_latest_image_rect.collidepoint(mouse_pos):
        draw_button(button_latest_image_rect, button_latest_image_text, BUTTON_HOVER_COLOR)
    else:
        draw_button(button_latest_image_rect, button_latest_image_text, BUTTON_COLOR)

def draw_history_section():
    title_text = title_font.render("Date", True, HEADER_COLOR)
    screen.blit(title_text, title_text.get_rect(center=(width // 2, 100)))
    Image_text = title_font.render("Image", True, HEADER_COLOR)
    screen.blit(Image_text, Image_text.get_rect(topleft=(width // 100, 100)))
    Response_text = title_font.render("Response", True, HEADER_COLOR)
    screen.blit(Response_text, Response_text.get_rect(topright=(width - 10, 100)))

    # Draw date options only if a date hasn't been selected
    if selected_date is None:
        mouse_pos = pygame.mouse.get_pos()
        for i, date in enumerate(dates):
            date_button_rect = date_buttons[i]
            if date_button_rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, BUTTON_HOVER_COLOR, date_button_rect, border_radius=5)
            else:
                pygame.draw.rect(screen, BUTTON_COLOR, date_button_rect, border_radius=5)

            date_text = button_font.render(date, True, TEXT_COLOR)
            screen.blit(date_text, (date_button_rect.x + 10, date_button_rect.y + 5))

    # Display selected image and response if a date is clicked
    if selected_date:
        image_path = images[selected_date]
        response_text = responses[selected_date]
        Date_text = title_font.render(f"{selected_date}", True, HEADER_COLOR)
        screen.blit(Date_text, Date_text.get_rect(midtop=(width // 2, 150)))
        # Load and display image
        try:
            loaded_image = pygame.image.load(image_path)
            loaded_image = pygame.transform.scale(loaded_image, (200, 200))
            screen.blit(loaded_image, (width // 100, 200))  # Adjust position as needed
        except FileNotFoundError:
            error_text = button_font.render("Image not found", True, HEADER_COLOR)
            screen.blit(error_text, (width // 100, 200))

        # Display response text with wrapping
        wrapped_response_text = wrap_text(response_text, button_font, width // 5)  # Adjust width for wrapping
        for i, line in enumerate(wrapped_response_text):
            response_rendered = button_font.render(line, True, HEADER_COLOR)
            screen.blit(response_rendered, (width - 170, 200 + i * 30))  # Adjust position as needed

def wrap_text(text, font, max_width):
    """Wrap text to fit within a specified width."""
    words = text.split(' ')
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)  # Add the last line
    return lines

def draw_latest_image_section():
    # Fetch the latest record from the database
    latest_record = db.last()
    
    if latest_record:
        image_path = latest_record[0][0]  # Assuming the first column is the image path
        response_text = latest_record[0][1]  # Assuming the second column is the response
        text = title_font.render("Viewing Latest Image", True, HEADER_COLOR)
        screen.blit(text, text.get_rect(center=(width // 2, height // 2 - 100)))

        # Load and display the latest image
        try:
            loaded_image = pygame.image.load(image_path)
            loaded_image = pygame.transform.scale(loaded_image, (200, 200))
            screen.blit(loaded_image, (width // 100, height // 2))  # Adjust position as needed
        except FileNotFoundError:
            error_text = button_font.render("Image not found", True, HEADER_COLOR)
            screen.blit(error_text, (width // 100, height // 2))

        # Display the latest response text with wrapping
        wrapped_response_text = wrap_text(response_text, button_font, width // 5)  # Adjust width for wrapping
        for i, line in enumerate(wrapped_response_text):
            response_rendered = button_font.render(line, True, HEADER_COLOR)
            screen.blit(response_rendered, (width - 170, height // 2 + 220 + i * 30))  # Adjust position as needed
    else:
        error_text = button_font.render("No latest image available", True, HEADER_COLOR)
        screen.blit(error_text, (width // 2 - 100, height // 2))

# Main loop
running = True
while running:
    # Draw home page and conditionally draw additional sections
    draw_home_page()
    if show_history:
        draw_history_section()
    elif show_latest_image:
        draw_latest_image_section()

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Home page button clicks
            if button_history_rect.collidepoint(event.pos):
                show_history = not show_history  # Toggle history display
                show_latest_image = False        # Hide latest image when showing history
                selected_date = None             # Reset selected date when toggling history
            elif button_latest_image_rect.collidepoint(event.pos):
                show_latest_image = not show_latest_image  # Toggle latest image display
                show_history = False  # Hide history when showing latest image

            # Date button clicks when history is active
            if show_history and selected_date is None:  # Only check date buttons if no date is selected
                for i, date_button_rect in enumerate(date_buttons):
                    if date_button_rect.collidepoint(event.pos):
                        selected_date = dates[i]  # Set the selected date
                        # Call the record method to get image and response for the selected date
                        record_data = db.record(selected_date)
                        if record_data:
                            images[selected_date] = record_data[0][0]  # Update image path
                            responses[selected_date] = record_data[0][1]  # Update response

    pygame.display.flip()  # Update the display

# Quit Pygame
pygame.quit()
sys.exit()
