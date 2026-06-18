CREATE TABLE IF NOT EXISTS rooms (
    room_id SERIAL PRIMARY KEY,
    room_number VARCHAR(10) NOT NULL UNIQUE,
    room_type VARCHAR(50) NOT NULL,
    rate_per_night NUMERIC(10,2) NOT NULL,
    max_occupancy INT NOT NULL DEFAULT 2,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS bookings (
    booking_id SERIAL PRIMARY KEY,
    guest_name VARCHAR(100) NOT NULL,
    id_number VARCHAR(50) NOT NULL,
    room_id INT NOT NULL REFERENCES rooms(room_id),
    booked_checkin_date DATE NOT NULL,
    booked_checkout_date DATE NOT NULL,
    actual_checkin_ts TIMESTAMPTZ,
    actual_checkout_ts TIMESTAMPTZ,
    digital_key VARCHAR(10),
    status VARCHAR(20) NOT NULL DEFAULT 'BOOKED',
    special_requests TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT valid_dates CHECK (booked_checkout_date > booked_checkin_date),
    CONSTRAINT valid_status CHECK (status IN ('BOOKED','CHECKED_IN','CHECKED_OUT','CANCELLED'))
);

CREATE TABLE IF NOT EXISTS bills (
    bill_id SERIAL PRIMARY KEY,
    booking_id INT NOT NULL REFERENCES bookings(booking_id) UNIQUE,
    booked_nights INT NOT NULL,
    actual_nights INT NOT NULL,
    rate_per_night NUMERIC(10,2) NOT NULL,
    base_amount NUMERIC(10,2) NOT NULL,
    late_checkout_hours NUMERIC(5,2) NOT NULL DEFAULT 0,
    late_fine NUMERIC(10,2) NOT NULL DEFAULT 0,
    total_amount NUMERIC(10,2) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_bookings_guest_name ON bookings(LOWER(guest_name));
CREATE INDEX IF NOT EXISTS idx_bookings_id_number ON bookings(id_number);
CREATE INDEX IF NOT EXISTS idx_bookings_status ON bookings(status);
CREATE INDEX IF NOT EXISTS idx_bookings_room_dates ON bookings(room_id, booked_checkin_date, booked_checkout_date);

INSERT INTO rooms (room_number, room_type, rate_per_night, max_occupancy, description) VALUES
    ('101', 'Standard', 3500.00, 2, 'Ground floor garden view king bed'),
    ('102', 'Standard', 3500.00, 2, 'Ground floor garden view twin beds'),
    ('103', 'Standard', 3500.00, 2, 'Ground floor courtyard view king bed'),
    ('201', 'Deluxe', 5500.00, 2, 'City view king bed work desk'),
    ('202', 'Deluxe', 5500.00, 3, 'City view two queen beds'),
    ('203', 'Deluxe', 5500.00, 2, 'Pool view king bed balcony'),
    ('301', 'Suite', 9500.00, 4, 'Corner suite panoramic view living room'),
    ('302', 'Suite', 9500.00, 4, 'Executive suite kitchenette two bedrooms'),
    ('401', 'Penthouse', 18000.00, 6, 'Full floor private terrace butler service'),
    ('104', 'Standard', 3500.00, 2, 'Ground floor accessible room')
ON CONFLICT (room_number) DO NOTHING;