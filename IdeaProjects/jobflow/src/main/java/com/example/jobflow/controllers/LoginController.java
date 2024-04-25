package com.example.jobflow.controllers;

import com.example.jobflow.MainApp;
import com.example.jobflow.entities.User;
import com.example.jobflow.services.UserService;
import com.example.jobflow.utils.AlertUtils;
import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.control.Button;
import javafx.scene.control.PasswordField;
import javafx.scene.control.TextField;

import java.net.URL;
import java.util.ResourceBundle;

public class LoginController implements Initializable {

    @FXML
    public TextField inputEmail;
    @FXML
    public PasswordField inputPassword;
    @FXML
    public Button btnSignup;

    @Override
    public void initialize(URL url, ResourceBundle rb) {
    }


    public void signUp(ActionEvent ignored) {
        MainApp.getInstance().loadSignup();
    }

    public void login(ActionEvent ignored) {
        User user = UserService.getInstance().checkUser(inputEmail.getText(), inputPassword.getText());

        if (user != null) {
            MainApp.getInstance().login(user);
        } else {
            AlertUtils.makeError("Identifiants invalides");
        }
    }

    @FXML
    public void back(ActionEvent ignored) {
        MainApp.getInstance().loadBack();
    }
}
