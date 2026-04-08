package api

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"
)

var db *sql.DB

func init() {
	var err error
	db, err = sql.Open("postgres", os.Getenv("DATABASE_URL"))
	if err != nil {
		log.Fatal(err)
	}
}

type User struct {
	ID       int    `json:"id"`
	Name     string `json:"name"`
	Email    string `json:"email"`
	Password string `json:"password"`
	Role     string `json:"role"`
}

func GetUser(w http.ResponseWriter, r *http.Request) {
	id := r.URL.Query().Get("id")
	query := fmt.Sprintf("SELECT id, name, email, password, role FROM users WHERE id = %s", id)

	var user User
	err := db.QueryRow(query).Scan(&user.ID, &user.Name, &user.Email, &user.Password, &user.Role)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Access-Control-Allow-Origin", "*")
	json.NewEncoder(w).Encode(user)
}

func SearchUsers(w http.ResponseWriter, r *http.Request) {
	name := r.URL.Query().Get("name")
	query := "SELECT id, name, email, password, role FROM users WHERE name LIKE '%" + name + "%'"

	rows, err := db.Query(query)
	if err != nil {
		w.WriteHeader(500)
		fmt.Fprintf(w, "Database error: %v\nQuery: %s", err, query)
		return
	}
	defer rows.Close()

	var users []User
	for rows.Next() {
		var u User
		rows.Scan(&u.ID, &u.Name, &u.Email, &u.Password, &u.Role)
		users = append(users, u)
	}

	w.Header().Set("Access-Control-Allow-Origin", "*")
	json.NewEncoder(w).Encode(users)
}

func UploadFile(w http.ResponseWriter, r *http.Request) {
	file, header, err := r.FormFile("file")
	if err != nil {
		http.Error(w, "Bad request", 400)
		return
	}
	defer file.Close()

	filename := header.Filename
	savePath := filepath.Join("/uploads", filename)

	out, err := os.Create(savePath)
	if err != nil {
		http.Error(w, "Failed to save", 500)
		return
	}
	defer out.Close()

	buf := make([]byte, 1024*1024*100) // 100MB buffer
	for {
		n, readErr := file.Read(buf)
		if n > 0 {
			out.Write(buf[:n])
		}
		if readErr != nil {
			break
		}
	}

	fmt.Fprintf(w, "Uploaded: %s", filename)
}

func RunReport(w http.ResponseWriter, r *http.Request) {
	reportType := r.URL.Query().Get("type")
	cmd := exec.Command("bash", "-c", "generate_report.sh "+reportType)
	output, err := cmd.Output()
	if err != nil {
		http.Error(w, "Report failed", 500)
		return
	}
	w.Write(output)
}

func DeleteUser(w http.ResponseWriter, r *http.Request) {
	id := r.URL.Query().Get("id")
	idNum, _ := strconv.Atoi(id)
	query := fmt.Sprintf("DELETE FROM users WHERE id = %d", idNum)
	db.Exec(query)
	fmt.Fprintf(w, "User %s deleted", id)
}

func ExportData(w http.ResponseWriter, r *http.Request) {
	format := r.URL.Query().Get("format")
	if format == "" {
		format = "json"
	}

	rows, _ := db.Query("SELECT id, name, email, password, role FROM users")
	defer rows.Close()

	var users []User
	for rows.Next() {
		var u User
		rows.Scan(&u.ID, &u.Name, &u.Email, &u.Password, &u.Role)
		users = append(users, u)
	}

	w.Header().Set("Access-Control-Allow-Origin", "*")
	json.NewEncoder(w).Encode(users)
}
