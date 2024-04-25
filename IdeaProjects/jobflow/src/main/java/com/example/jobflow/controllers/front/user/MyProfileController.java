package com.example.jobflow.controllers.front.user;

import com.example.jobflow.MainApp;
import com.example.jobflow.controllers.front.MainWindowController;
import com.example.jobflow.entities.User;
import com.example.jobflow.utils.Constants;
import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.control.Button;
import javafx.scene.text.Text;

import java.net.URL;
import java.util.ResourceBundle;

public class MyProfileController implements Initializable {

    public static User currentUser;

    @FXML
    public Text emailText;
    @FXML
    public Text lastnameText;
    @FXML
    public Text rolesText;
    @FXML
    public Text statusText;


    @FXML
    public Text topText;
    @FXML
    public Button addButton;

    @Override
    public void initialize(URL url, ResourceBundle rb) {
        User user = MainApp.getSession();

        emailText.setText("Email : " + user.getEmail());
        lastnameText.setText("Lastname : " + user.getLastname());
        rolesText.setText("Roles : " + user.getRoles());
        statusText.setText("Status : " + user.getStatus());
    }

    @FXML
    public void editProfile(ActionEvent ignored) {
        currentUser = MainApp.getSession();
        MainWindowController.getInstance().loadInterface(Constants.FXML_FRONT_EDIT_PROFILE);
    }
}
