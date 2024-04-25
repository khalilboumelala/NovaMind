package com.example.jobflow.controllers.front.user;

import com.example.jobflow.MainApp;
import com.example.jobflow.controllers.front.MainWindowController;
import com.example.jobflow.entities.User;
import com.example.jobflow.services.UserService;
import com.example.jobflow.utils.AlertUtils;
import com.example.jobflow.utils.Constants;
import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.control.Button;
import javafx.scene.control.TextField;
import javafx.scene.text.Text;

import java.net.URL;
import java.util.ResourceBundle;
import java.util.regex.Pattern;

public class EditProfileController implements Initializable {

    @FXML
    public TextField emailTF;
    @FXML
    public TextField lastnameTF;
    @FXML
    public Button btnAjout;
    @FXML
    public Text topText;

    User currentUser;


    @Override
    public void initialize(URL url, ResourceBundle rb) {

        currentUser = MainApp.getSession();

        topText.setText("Modifier mon profil");
        btnAjout.setText("Modifier");

        try {
            emailTF.setText(currentUser.getEmail());
            lastnameTF.setText(currentUser.getLastname());

        } catch (NullPointerException ignored) {
            System.out.println("NullPointerException");
        }
    }

    @FXML
    private void manage(ActionEvent ignored) {

        if (controleDeSaisie()) {

            User user = new User();
            user.setEmail(emailTF.getText());
            user.setLastname(lastnameTF.getText());
            user.setRoles("[\"ROLE_USER\"]");
            user.setStatus(1);

            user.setId(currentUser.getId());
            if (UserService.getInstance().edit(user)) {
                MainApp.setSession(user);
                AlertUtils.makeSuccessNotification("Profile modifié avec succés");
            } else {
                AlertUtils.makeError("Could not edit user");
            }


            MainWindowController.getInstance().loadInterface(Constants.FXML_FRONT_MY_PROFILE);
        }
    }


    private boolean controleDeSaisie() {


        if (emailTF.getText().isEmpty()) {
            AlertUtils.makeInformation("email ne doit pas etre vide");
            return false;
        }
        if (!Pattern.compile("^(.+)@(.+)$").matcher(emailTF.getText()).matches()) {
            AlertUtils.makeInformation("Email invalide");
            return false;
        }


        if (lastnameTF.getText().isEmpty()) {
            AlertUtils.makeInformation("lastname ne doit pas etre vide");
            return false;
        }

        return true;
    }
}