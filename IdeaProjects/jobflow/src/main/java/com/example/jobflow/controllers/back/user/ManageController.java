package com.example.jobflow.controllers.back.user;


import com.example.jobflow.controllers.back.MainWindowController;
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

public class ManageController implements Initializable {

    @FXML
    public TextField emailTF;
    @FXML
    public TextField lastnameTF;
    @FXML
    public TextField rolesTF;
    @FXML
    public TextField statusTF;


    @FXML
    public Button btnAjout;
    @FXML
    public Text topText;

    User currentUser;


    @Override
    public void initialize(URL url, ResourceBundle rb) {

        currentUser = ShowAllController.currentUser;

        if (currentUser != null) {
            topText.setText("Modifier user");
            btnAjout.setText("Modifier");

            try {
                emailTF.setText(currentUser.getEmail());
                lastnameTF.setText(currentUser.getLastname());
                rolesTF.setText(currentUser.getRoles());
                statusTF.setText(String.valueOf(currentUser.getStatus()));

            } catch (NullPointerException ignored) {
                System.out.println("NullPointerException");
            }
        } else {
            topText.setText("Ajouter user");
            btnAjout.setText("Ajouter");
        }
    }

    @FXML
    private void manage(ActionEvent ignored) {

        if (controleDeSaisie()) {

            User user = new User();
            user.setEmail(emailTF.getText());
            user.setLastname(lastnameTF.getText());
            user.setRoles(rolesTF.getText());
            user.setStatus(Integer.parseInt(statusTF.getText()));


            if (currentUser == null) {
                if (UserService.getInstance().add(user)) {
                    AlertUtils.makeSuccessNotification("User ajouté avec succés");
                    MainWindowController.getInstance().loadInterface(Constants.FXML_BACK_DISPLAY_ALL_USER);
                } else {
                    AlertUtils.makeError("Error");
                }
            } else {
                user.setId(currentUser.getId());
                if (UserService.getInstance().edit(user)) {
                    AlertUtils.makeSuccessNotification("User modifié avec succés");
                    ShowAllController.currentUser = null;
                    MainWindowController.getInstance().loadInterface(Constants.FXML_BACK_DISPLAY_ALL_USER);
                } else {
                    AlertUtils.makeError("Error");
                }
            }

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


        if (rolesTF.getText().isEmpty()) {
            AlertUtils.makeInformation("roles ne doit pas etre vide");
            return false;
        }


        if (statusTF.getText().isEmpty()) {
            AlertUtils.makeInformation("status ne doit pas etre vide");
            return false;
        }


        try {
            Integer.parseInt(statusTF.getText());
        } catch (NumberFormatException ignored) {
            AlertUtils.makeInformation("status doit etre un nombre");
            return false;
        }

        return true;
    }
}