module com.example.jobflow {
    requires javafx.controls;
    requires javafx.fxml;
    requires java.sql;
    requires jbcrypt;

    opens com.example.jobflow to javafx.fxml;
    opens com.example.jobflow.entities to javafx.fxml;
    opens com.example.jobflow.controllers to javafx.fxml;
    opens com.example.jobflow.controllers.back to javafx.fxml;
    opens com.example.jobflow.controllers.front to javafx.fxml;
    opens com.example.jobflow.controllers.front.user to javafx.fxml;
    opens com.example.jobflow.controllers.back.user to javafx.fxml;

    exports com.example.jobflow;
    exports com.example.jobflow.entities;
    exports com.example.jobflow.controllers;
    exports com.example.jobflow.controllers.back;
    exports com.example.jobflow.controllers.front;
    exports com.example.jobflow.controllers.front.user;
    exports com.example.jobflow.controllers.back.user;
}