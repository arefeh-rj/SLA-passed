INSERT INTO users (display_name, email, phone_e164, is_phone_verified)
VALUES
  ('arefe ', 'rajabian.arefeh79@gmail.com', '989334522831', true),
  ('nargess', 'rajabian.arefeh99@gmail.com', '989024610775', false)
ON CONFLICT DO NOTHING;
