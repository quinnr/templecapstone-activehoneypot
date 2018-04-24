package model.attacker;

import dbUtils.*;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.ArrayList;

public class StringDataList {

    public String dbError = "";
    private ArrayList<StringData> recordList = new ArrayList();

    // Default constructor just leaves the 2 data members initialized as above
    public StringDataList() {
    }

    // overloaded constructor populates the list (and possibly the dbError)
    public StringDataList(String attackerNameStartsWith, DbConn dbc, String searchBy) {

        StringData sd = new StringData();

        System.out.println("Searching for champions that start with " + attackerNameStartsWith);

        try {
            String sql;
            if (searchBy.equals("state")) {
                sql = "SELECT attackerID, ip_address, username, passwords, time_of_day_accessed, logFile, "
                        + "sessions, country, city, state, logged_in, uploaded_files, date_accessed, latitude, longitude FROM attacker "
                        + " WHERE state LIKE ? ORDER BY attackerID DESC";
            } else if (searchBy.equals("city")) {
                sql = "SELECT attackerID, ip_address, username, passwords, time_of_day_accessed, logFile, "
                        + "sessions, country, city, state, logged_in, uploaded_files, date_accessed, latitude, longitude FROM attacker "
                        + " WHERE city LIKE ? ORDER BY attackerID DESC";
            } else if (searchBy.equals("ip")) {
                sql = "SELECT attackerID, ip_address, username, passwords, time_of_day_accessed, logFile, "
                        + "sessions, country, city, state, logged_in, uploaded_files, date_accessed, latitude, longitude FROM attacker "
                        + " WHERE ip_address LIKE ? ORDER BY attackerID DESC";
            } else {
                sql = "SELECT attackerID, ip_address, username, passwords, time_of_day_accessed, logFile, "
                        + "sessions, country, city, state, logged_in, uploaded_files, date_accessed, latitude, longitude FROM attacker "
                        + " WHERE country LIKE ? ORDER BY attackerID DESC";
            }
            PreparedStatement stmt = dbc.getConn().prepareStatement(sql);
            stmt.setString(1, attackerNameStartsWith + "%");
            ResultSet results = stmt.executeQuery();

            while (results.next()) {
                try {
                    sd = new StringData();
                    sd.attackerID = FormatUtils.formatInteger(results.getObject("attackerID"));
                    sd.ip_address = FormatUtils.formatString(results.getObject("ip_address"));
                    sd.username = FormatUtils.formatString(results.getObject("username"));
                    sd.passwords = FormatUtils.formatString(results.getObject("passwords"));
                    sd.time_of_day_accessed = FormatUtils.formatTime(results.getObject("time_of_day_accessed"));
                    sd.logFile = FormatUtils.formatString(results.getObject("logFile"));
                    sd.sessions = FormatUtils.formatInteger(results.getObject("sessions"));
                    sd.country = FormatUtils.formatString(results.getObject("country"));
                    sd.city = FormatUtils.formatString(results.getObject("city"));
                    sd.state = FormatUtils.formatString(results.getObject("state"));
                    sd.latitude = FormatUtils.formatString(results.getObject("latitude"));
                    sd.longitude = FormatUtils.formatString(results.getObject("longitude"));
                    //logged_in
                    //uplaoded_files
                    sd.date_accessed = FormatUtils.formatDate(results.getObject("date_accessed"));
                    this.recordList.add(sd);
                } catch (Exception e) {
                    sd.errorMsg = "Record Level Error in model.Attacker.StringDataList Constructor: " + e.getMessage();
                    this.recordList.add(sd);
                }
            } // while
        } catch (Exception e) {
            this.dbError = "List Level Error in model.Attacker.StringDataList Constructor: " + e.getMessage();
        }
    } // method

} // class
