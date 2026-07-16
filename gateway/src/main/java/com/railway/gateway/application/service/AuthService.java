package com.railway.gateway.application.service;

import com.railway.gateway.api.dto.LoginRequest;
import com.railway.gateway.api.dto.LoginResponse;
import com.railway.gateway.api.dto.RefreshTokenRequest;
import com.railway.gateway.api.dto.RefreshTokenResponse;
import com.railway.gateway.api.dto.RegisterRequest;
import com.railway.gateway.api.dto.LoginResponse;

public interface AuthService {

    LoginResponse register(RegisterRequest request);

    LoginResponse login(LoginRequest request);

    RefreshTokenResponse refresh(RefreshTokenRequest request);

    void logout(String refreshToken);
}