#include "esp_camera.h"
#include <stdlib.h>
#include <WiFi.h>
#include <ESP32_FTPClient.h>

// Camera configuration
#define CAMERA_MODEL_AI_THINKER
#include "camera_pins.h"

// Enter your WiFi credentials
const char *ssid = "DuckTape";      // DuckTape
const char *password = "DuckTape1"; // DuckTape1

// FTP server credentials
char* ftp_ip = "10.42.0.1";         // 10.42.0.1
char* ftp_user = "testuser";        // testuser
char* ftp_pass = "1";               // 1

// Motion detection parameters
int motion_min = 4500;
int motion_max = 8000;

// Variables for frame comparison
uint8_t* prev_frame = nullptr;
size_t prev_frame_len = 0;

// Function Prototypes
int frameDifference(uint8_t* frame1, size_t len1, uint8_t* frame2, size_t len2);
int frameDifferenceN(uint8_t* frame1, size_t len1, uint8_t* frame2, size_t len2);

// Create FTP client instance
ESP32_FTPClient ftp(ftp_ip, ftp_user, ftp_pass);

// Image counter
int ctr;

///// Main /////
void setup() {
  Serial.begin(115200);

  // Initialize camera
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;

  // Frame size and image quality
  config.frame_size = FRAMESIZE_VGA;
  config.jpeg_quality = 4;
  config.fb_count = 1;

  // Initialize camera
  if (esp_camera_init(&config) != ESP_OK) {
    Serial.println("Camera init failed");
    return;
  }

  // Configure camera settings for consistency of images
  sensor_t * s = esp_camera_sensor_get();
  s->set_vflip(s, 1);                        // flip camera perespective vertically
  s->set_framesize(s, FRAMESIZE_VGA);       // resolution
  s->set_quality(s, 4);                      // quality level
  s->set_brightness(s, 0);                   // brightness
  s->set_contrast(s, 0);                     // contrast
  s->set_whitebal(s, 0);                     // auto white balance
  s->set_gain_ctrl(s, 0);                    // gain control
  s->set_exposure_ctrl(s, 0);                // exposure control

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("Connected to Wifi");

  delay(250);
}

void loop() {

  // Capture current frame
  camera_fb_t* current_frame = esp_camera_fb_get();
  delay(300);
  if (!current_frame) {
    Serial.println("Failed to capture frame");
  }

  else {
    if (prev_frame) {
      // Get frame difference
      int difference = frameDifferenceN(prev_frame, prev_frame_len, current_frame->buf, current_frame->len);
      Serial.print("Difference = ");
      Serial.println(difference);

      // Check for high differnce
      if (difference > motion_min &
          difference < motion_max) {
        Serial.println("Motion detected!");

        // Connect with ftp
        ftp.OpenConnection();
        ftp.InitFile("Type I");
        ftp.ChangeWorkDir("/");

        // Give image a unique name
        char name[30];
        sprintf(name, "motion_image%d.jpg", ctr);
        ctr += 1;
        ftp.NewFile(name);

        // Send file and close ftp
        ftp.WriteData(current_frame->buf, current_frame->len);
        ftp.CloseFile();
        ftp.CloseConnection();

        Serial.println("Image uploaded to FTP");

        delay(5000); // long delay before motion can be detected again
      }

      // Free the previous frame memory
      free(prev_frame);
    }

    // Store current frame as previous frame for the next iteration
    prev_frame = (uint8_t*)malloc(current_frame->len);
    if (prev_frame) {
      memcpy(prev_frame, current_frame->buf, current_frame->len);
      prev_frame_len = current_frame->len;
      delay(300);
    }

    // Return the frame buffer back to the driver for reuse
    esp_camera_fb_return(current_frame);

    delay(250); // short delay
  }
}

///// End of Main /////



// Functions

// Function to calculate frame difference of every 10th pixel
int frameDifference(uint8_t* frame1, size_t len1, uint8_t* frame2, size_t len2) {
  int diff, pixel1, pixel2;
  if (len1 != len2) {
    Serial.println("Frame size mismatch detected");
    Serial.print("len1 = ");
    Serial.println(len1);
    Serial.print("len2 = ");
    Serial.println(len2);
    return 0;
  }

  diff = 0;

  // Iterate over the bytes, sampling every 20th pixel to reduce sensitivity
  for (size_t i = 0; i < len1; i += 20) {
    pixel1 = (frame1[i] + frame1[i + 1] + frame1[i + 2]) / 3; // Grayscale approximation for RGB
    pixel2 = (frame2[i] + frame2[i + 1] + frame2[i + 2]) / 3; 
    diff += abs(pixel1 - pixel2);
  }

  return diff;
}

int frameDifferenceN(uint8_t* frame1, size_t len1, uint8_t* frame2, size_t len2) {
  int diff, pixel1, pixel2, value1, value2;
  size_t ifactor1, ifactor2;
  ifactor1 = len1 / 100;
  ifactor2 = len2 / 100;

  diff = 0;

  // Iterate over the bytes, sampling every 20th pixel to reduce sensitivity
  for (size_t i = 0; i*ifactor1 < len1 & i*ifactor2 < len2; i++) {
    pixel1 = i * ifactor1;
    pixel2 = i * ifactor2;

    value1 = (frame1[pixel1] + frame1[pixel1 + 1] + frame1[pixel1 + 2]) / 3; // Grayscale approximation for RGB
    value2 = (frame2[pixel1] + frame2[pixel1 + 1] + frame2[pixel1 + 2]) / 3;

    diff += abs(value1 - value2);
  }

  return diff;
}