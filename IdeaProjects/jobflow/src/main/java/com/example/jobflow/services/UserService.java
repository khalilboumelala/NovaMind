package com.example.jobflow.services;

import com.example.jobflow.entities.User;
import com.example.jobflow.utils.DatabaseConnection;
import org.mindrot.jbcrypt.BCrypt;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

public class UserService {

    private static UserService instance;
    PreparedStatement preparedStatement;
    Connection connection;

    public UserService() {
        connection = DatabaseConnection.getInstance().getConnection();
    }

    public static UserService getInstance() {
        if (instance == null) {
            instance = new UserService();
        }
        return instance;
    }

    public User checkUser(String email, String password) {

        try {
            preparedStatement = connection.prepareStatement("SELECT * FROM user WHERE `email` LIKE ?");

            preparedStatement.setString(1, email);
            ResultSet resultSet = preparedStatement.executeQuery();

            if (resultSet.next()) {
                User user = new User();
                user.setId(resultSet.getInt("id"));
                user.setEmail(resultSet.getString("email"));
                user.setPassword(resultSet.getString("password"));
                user.setLastname(resultSet.getString("lastname"));
                user.setRoles(resultSet.getString("roles"));
                user.setStatus(resultSet.getInt("status"));

                return checkPassword(password, user.getPassword()) ? user : null;
            }

        } catch (SQLException e) {
            System.out.println("Aucun email : " + e.getMessage());
        }

        return null;
    }


    private Boolean checkPassword(String inputPassword, String hashedPasswordFromDatabase) {
        try {
            return BCrypt.checkpw(inputPassword, hashedPasswordFromDatabase);
        } catch (Exception e) {
            System.out.println("Error (checkPassword) : " + e.getMessage());
        }
        return false;
    }

    private String encodePassword(String password) {
        return BCrypt.hashpw(password, BCrypt.gensalt(13));
    }

    public List<User> getAll() {
        List<User> listUser = new ArrayList<>();
        try {

            preparedStatement = connection.prepareStatement("SELECT * FROM `user`");


            ResultSet resultSet = preparedStatement.executeQuery();

            while (resultSet.next()) {
                User user = new User();
                user.setId(resultSet.getInt("id"));
                user.setEmail(resultSet.getString("email"));
                user.setPassword(resultSet.getString("password"));
                user.setLastname(resultSet.getString("lastname"));
                user.setRoles(resultSet.getString("roles"));
                user.setStatus(resultSet.getInt("status"));

                listUser.add(user);
            }
        } catch (SQLException exception) {
            System.out.println("Error (getAll) user : " + exception.getMessage());
        }
        return listUser;
    }


    public boolean add(User user) {


        String request = "INSERT INTO `user`(`email`, `password`, `lastname`, `roles`, `status`) VALUES(?, ?, ?, ?, ?)";

        try {
            preparedStatement = connection.prepareStatement(request);

            preparedStatement.setString(1, user.getEmail());
            preparedStatement.setString(2, encodePassword(user.getPassword()));
            preparedStatement.setString(3, user.getLastname());
            preparedStatement.setString(4, user.getRoles());
            preparedStatement.setInt(5, user.getStatus());


            preparedStatement.executeUpdate();
            System.out.println("User added");
            return true;
        } catch (SQLException exception) {
            System.out.println("Error (add) user : " + exception.getMessage());
        }
        return false;
    }

    public boolean edit(User user) {

        String request = "UPDATE `user` SET `email` = ?, `lastname` = ?, `roles` = ?, `status` = ? WHERE `id` = ?";

        try {
            preparedStatement = connection.prepareStatement(request);

            preparedStatement.setString(1, user.getEmail());

            preparedStatement.setString(2, user.getLastname());
            preparedStatement.setString(3, user.getRoles());
            preparedStatement.setInt(4, user.getStatus());

            preparedStatement.setInt(5, user.getId());

            preparedStatement.executeUpdate();
            System.out.println("User edited");
            return true;
        } catch (SQLException exception) {
            System.out.println("Error (edit) user : " + exception.getMessage());
        }
        return false;
    }

    public boolean delete(int id) {
        try {
            preparedStatement = connection.prepareStatement("DELETE FROM `user` WHERE `id`=?");
            preparedStatement.setInt(1, id);

            preparedStatement.executeUpdate();
            preparedStatement.close();
            System.out.println("User deleted");
            return true;
        } catch (SQLException exception) {
            System.out.println("Error (delete) user : " + exception.getMessage());
        }
        return false;
    }
}
