import database
import face_utils
import attendance_logic
from datetime import datetime
import pandas as pd
import config


class StaffService:
    @staticmethod
    def register_staff(staff_id, name, mobile, email, dept, role, face_encoding):
        """Register a new staff member."""
        conn = database.get_connection()
        c = conn.cursor()
        try:
            c.execute(
                """
                INSERT INTO staff (staff_id, name, mobile_number, email, department, role, face_encoding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (staff_id, name, mobile, email, dept, role, face_encoding),
            )
            conn.commit()
            return True, f"Staff {name} ({staff_id}) registered successfully!"
        except Exception as e:
            return False, f"Error saving to database: {e}"
        finally:
            conn.close()

    @staticmethod
    def get_all_staff():
        """Get all staff data."""
        conn = database.get_connection()
        df = pd.read_sql_query("SELECT * FROM staff", conn)
        conn.close()
        return df

    @staticmethod
    def update_staff(staff_id, name, mobile, email, dept, role):
        """Update an existing staff member's details (except face_encoding)."""
        conn = database.get_connection()
        c = conn.cursor()
        try:
            c.execute(
                """
                UPDATE staff
                SET name=?, mobile_number=?, email=?, department=?, role=?
                WHERE staff_id=?
            """,
                (name, mobile, email, dept, role, staff_id),
            )
            conn.commit()
            return True, "Staff updated successfully"
        except Exception as e:
            return False, f"Error updating staff: {e}"
        finally:
            conn.close()

    @staticmethod
    def delete_staff(staff_id):
        """Remove a staff record from the database."""
        conn = database.get_connection()
        c = conn.cursor()
        try:
            c.execute("DELETE FROM staff WHERE staff_id=?", (staff_id,))
            conn.commit()
            return True, "Staff deleted successfully"
        except Exception as e:
            return False, f"Error deleting staff: {e}"
        finally:
            conn.close()

    @staticmethod
    def get_staff_for_face_recognition():
        """Get staff data for face recognition."""
        conn = database.get_connection()
        c = conn.cursor()
        c.execute("SELECT staff_id, name, face_encoding FROM staff")
        rows = c.fetchall()
        conn.close()

        known_ids = []
        known_names = []
        known_encodings = []

        for row in rows:
            known_ids.append(row[0])
            known_names.append(row[1])
            encoding_blob = row[2]

            if isinstance(encoding_blob, bytes):
                try:
                    encoding = database.convert_array(encoding_blob)
                    known_encodings.append(encoding)
                except Exception as e:
                    print(f"Error loading face for {row[1]}: {e}")
                    known_ids.pop()
                    known_names.pop()
            else:
                known_encodings.append(encoding_blob)

        return known_ids, known_names, known_encodings


class AttendanceService:
    @staticmethod
    def mark_attendance(staff_id, name, current_date, current_time):
        """Mark attendance for a staff member."""
        conn = database.get_connection()
        c = conn.cursor()

        try:
            # Fetch existing attendance for today
            c.execute(
                "SELECT in_time, out_time FROM attendance WHERE staff_id=? AND punch_date=?",
                (staff_id, current_date),
            )
            att_record = c.fetchone()

            # Fetch counters
            month_str = current_date.strftime("%Y-%m")
            c.execute(
                "SELECT grace_count, late_count, permission_count FROM counters WHERE staff_id=? AND month_str=?",
                (staff_id, month_str),
            )
            counters = c.fetchone()
            if not counters:
                # Initialize counters if not exist
                c.execute(
                    "INSERT INTO counters (staff_id, month_str) VALUES (?, ?)",
                    (staff_id, month_str),
                )
                conn.commit()
                counters = (0, 0, 0)

            counters_dict = {
                "grace": counters[0],
                "late": counters[1],
                "permission": counters[2],
            }

            if not att_record:
                # PUNCH IN
                result = attendance_logic.check_in_status(current_time, counters_dict)
                status = result["status"]
                updates = result["updates"]

                # Update Counters
                if updates["grace"]:
                    c.execute(
                        "UPDATE counters SET grace_count = grace_count + 1 WHERE staff_id=? AND month_str=?",
                        (staff_id, month_str),
                    )
                if updates["late"]:
                    c.execute(
                        "UPDATE counters SET late_count = late_count + 1 WHERE staff_id=? AND month_str=?",
                        (staff_id, month_str),
                    )
                if updates["permission"]:
                    c.execute(
                        "UPDATE counters SET permission_count = permission_count + 1 WHERE staff_id=? AND month_str=?",
                        (staff_id, month_str),
                    )

                # Insert Attendance
                c.execute(
                    "INSERT INTO attendance (staff_id, punch_date, in_time, status) VALUES (?, ?, ?, ?)",
                    (staff_id, current_date, current_time.strftime("%H:%M:%S"), status),
                )
                conn.commit()
                return (
                    True,
                    f"Punch In Successful at {current_time.strftime('%H:%M:%S')}! Status: {status}",
                )

            else:
                # ALREADY PUNCHED IN
                in_time_str = att_record[0]
                out_time_str = att_record[1]

                if out_time_str:
                    return (
                        False,
                        f"Already Punched Out at {out_time_str}. Have a nice day!",
                    )
                else:
                    # PUNCH OUT
                    status = attendance_logic.check_out_status(current_time)
                    c.execute(
                        "UPDATE attendance SET out_time=?, status=? WHERE staff_id=? AND punch_date=?",
                        (
                            current_time.strftime("%H:%M:%S"),
                            status,
                            staff_id,
                            current_date,
                        ),
                    )
                    conn.commit()
                    return (
                        True,
                        f"Punch Out Successful at {current_time.strftime('%H:%M:%S')}! Status: {status}",
                    )
        except Exception as e:
            return False, f"Error: {e}"
        finally:
            conn.close()

    @staticmethod
    def get_daily_attendance(date_sel):
        """Get attendance for a specific date."""
        conn = database.get_connection()
        query = """
        SELECT a.punch_date, a.in_time, a.out_time, a.status, s.name, s.department 
        FROM attendance a
        JOIN staff s ON a.staff_id = s.staff_id
        WHERE a.punch_date = ?
        """
        df = pd.read_sql_query(query, conn, params=(date_sel,))
        conn.close()
        return df

    @staticmethod
    def get_staff_history(staff_id):
        """Get attendance history for a staff member."""
        conn = database.get_connection()
        hist_query = "SELECT punch_date, in_time, out_time, status FROM attendance WHERE staff_id = ? ORDER BY punch_date DESC"
        df = pd.read_sql_query(hist_query, conn, params=(staff_id,))
        conn.close()
        return df

    @staticmethod
    def get_staff_counters(staff_id, month_str):
        """Get counters for a staff member."""
        conn = database.get_connection()
        c = conn.cursor()
        cnt_query = "SELECT grace_count, late_count, permission_count FROM counters WHERE staff_id = ? AND month_str = ?"
        c.execute(cnt_query, (staff_id, month_str))
        counts = c.fetchone()
        conn.close()
        return counts

    @staticmethod
    def update_attendance_record(staff_id, date, in_time, status):
        """Update an attendance record."""
        conn = database.get_connection()
        c = conn.cursor()
        try:
            # Check if exists
            c.execute(
                "SELECT id FROM attendance WHERE staff_id=? AND punch_date=?",
                (staff_id, date),
            )
            exists = c.fetchone()

            if exists:
                c.execute(
                    "UPDATE attendance SET in_time=?, status=? WHERE id=?",
                    (str(in_time), status, exists[0]),
                )
                conn.commit()
                return True, "Updated successfully"
            else:
                return False, "Record does not exist."
        except Exception as e:
            return False, f"Error: {e}"
        finally:
            conn.close()


class FaceRecognitionService:
    @staticmethod
    def recognize_face(image_data):
        """Recognize face from image data."""
        try:
            img = face_utils.load_image_file(image_data)
            encodings = face_utils.get_face_encodings(img)

            if len(encodings) == 0:
                return None, "No face detected."
            elif len(encodings) > 1:
                return None, "Multiple faces detected."
            else:
                encoding = encodings[0]
                known_ids, known_names, known_encodings = (
                    StaffService.get_staff_for_face_recognition()
                )
                match_index = face_utils.match_face(encoding, known_encodings)

                if match_index is not None:
                    return (known_ids[match_index], known_names[match_index]), None
                else:
                    return None, "Face not recognized."
        except Exception as e:
            return None, f"Error: {e}"
