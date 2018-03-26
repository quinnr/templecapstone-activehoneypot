package dbUtils;

import java.sql.DriverManager;
import java.sql.Connection;

/**
 * Wrapper class for database connection. Constructor opens connection. Close
 * method closes connection.
 */
public class DbConn {

    private String errMsg = ""; // will remain "" unless error getting connection
    private java.sql.Connection conn = null;

    /**
     * Constructor - opens database connection to database
     */
    public DbConn() {
        this.connect();
    } // method

    /**
     * Open a connection to your database.
     */
    private void connect() {

        try {
            String DRIVER = "com.mysql.jdbc.Driver";
            Class.forName(DRIVER).newInstance();
            try {
                String  url = "jdbc:mysql://activehoneypot-instance1.c6cgtt72anqv.us-west-2.rds.amazonaws.com:3306/activehoneypotDB?user=ahpmaster&password=cscapstone";
                this.conn = DriverManager.getConnection(url);

            } catch (Exception e) { // cant get the connection
                this.errMsg = "problem getting connection:" + e.getMessage();
            }
        } catch (Exception e) { // cant get the driver...
            this.errMsg = "problem getting driver:" + e.getMessage();
        }
    } // method

    /* Returns database connection for use in SQL classes.  */
    public Connection getConn() {
        return this.conn;
    }

    /* Returns database connection error message or "" if there is none.  */
    public String getErr() {
        return this.errMsg;
    }

    /**
     * Close database connection.
     */
    public void close() {

        if (conn != null) {
            try {
                conn.close();
            } // try
            catch (Exception e) {
                // Don't care if connection was already closed. Do nothing.
            } // catch
        } // if
    } // method

    // try to close the database connection in case the JSP page forgets to do it.
    // supposedly this is not all that reliable, but wouldnt hurt....
    @Override
    protected void finalize() throws Throwable {
        super.finalize();
        this.close();
    }
} // class
