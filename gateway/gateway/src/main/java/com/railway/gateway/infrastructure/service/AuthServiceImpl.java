package com.railway.gateway.infrastructure.service;

import org.springframework.security.core.AuthenticationException;
import com.railway.gateway.api.dto.LoginRequest;
import com.railway.gateway.api.dto.LoginResponse;
import com.railway.gateway.api.dto.RefreshTokenRequest;
import com.railway.gateway.api.dto.RefreshTokenResponse;
import com.railway.gateway.api.dto.RegisterRequest;
import com.railway.gateway.application.service.AuthService;
import com.railway.gateway.domain.entity.RefreshToken;
import com.railway.gateway.domain.entity.User;
import com.railway.gateway.domain.enums.UserRole;
import com.railway.gateway.domain.exception.RefreshTokenNotFoundException;
import com.railway.gateway.domain.exception.application.EmailAlreadyExistsException;
import com.railway.gateway.domain.exception.application.InvalidCredentialsException;
import com.railway.gateway.domain.exception.application.RefreshTokenExpiredException;
import com.railway.gateway.domain.exception.application.UsernameAlreadyExistsException;
import com.railway.gateway.domain.repository.RefreshTokenRepository;
import com.railway.gateway.domain.repository.UserRepository;
import com.railway.gateway.infrastructure.properties.JwtProperties;
import com.railway.gateway.infrastructure.security.JwtTokenProvider;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;

@Slf4j
@Service
@RequiredArgsConstructor
public class AuthServiceImpl implements AuthService {

    private final UserRepository userRepository;
    private final RefreshTokenRepository refreshTokenRepository;
    private final JwtTokenProvider jwtTokenProvider;
    private final AuthenticationManager authenticationManager;
    private final PasswordEncoder passwordEncoder;
    private final JwtProperties jwtProperties;

    @Override
    @Transactional
    public LoginResponse register(RegisterRequest request) {
        log.info("Registering new user: username={}, email={}", request.username(), request.email());

        if (userRepository.existsByUsername(request.username())) {
            throw new UsernameAlreadyExistsException(request.username());
        }

        if (userRepository.existsByEmail(request.email())) {
            throw new EmailAlreadyExistsException(request.email());
        }

        User user = User.builder()
                .username(request.username())
                .email(request.email())
                .passwordHash(passwordEncoder.encode(request.password()))
                .firstName(request.firstName())
                .lastName(request.lastName())
                .role(UserRole.USER)
                .enabled(true)
                .build();

        user = userRepository.save(user);

        String accessToken = jwtTokenProvider.generateAccessToken(user.getId(), user.getUsername());
        String refreshToken = jwtTokenProvider.generateRefreshToken(user.getId());

        saveRefreshToken(user, refreshToken);

        log.info("User registered successfully: userId={}, username={}", user.getId(), user.getUsername());

        return new LoginResponse(accessToken, refreshToken, jwtProperties.getAccessTokenExpiration());
    }

    @Override
    @Transactional
    public LoginResponse login(LoginRequest request) {
        log.info("User login attempt: username={}", request.username());

        try {
            authenticationManager.authenticate(
                    new UsernamePasswordAuthenticationToken(request.username(), request.password())
            );
        } catch (AuthenticationException e) {
            throw new InvalidCredentialsException();
        }

        User user = userRepository.findByUsername(request.username())
                .orElseThrow(InvalidCredentialsException::new);

        String accessToken = jwtTokenProvider.generateAccessToken(user.getId(), user.getUsername());
        String refreshToken = jwtTokenProvider.generateRefreshToken(user.getId());

        refreshTokenRepository.revokeAllUserTokens(user.getId());
        saveRefreshToken(user, refreshToken);

        log.info("User logged in successfully: userId={}, username={}", user.getId(), user.getUsername());

        return new LoginResponse(accessToken, refreshToken, jwtProperties.getAccessTokenExpiration());
    }

    @Override
    @Transactional
    public RefreshTokenResponse refresh(RefreshTokenRequest request) {
        log.info("Token refresh attempt");

        RefreshToken storedToken = refreshTokenRepository.findByToken(request.refreshToken())
                .orElseThrow(() -> new RefreshTokenNotFoundException(request.refreshToken(), true));

        if (storedToken.isRevoked()) {
            refreshTokenRepository.revokeAllUserTokens(storedToken.getUser().getId());
            throw new RefreshTokenExpiredException("Refresh token has been revoked");
        }

        if (storedToken.getExpiresAt().isBefore(LocalDateTime.now())) {
            refreshTokenRepository.revokeAllUserTokens(storedToken.getUser().getId());
            throw new RefreshTokenExpiredException();
        }

        User user = storedToken.getUser();

        refreshTokenRepository.revokeAllUserTokens(user.getId());

        String newAccessToken = jwtTokenProvider.generateAccessToken(user.getId(), user.getUsername());
        String newRefreshToken = jwtTokenProvider.generateRefreshToken(user.getId());

        saveRefreshToken(user, newRefreshToken);

        log.info("Token refreshed successfully: userId={}", user.getId());

        return new RefreshTokenResponse(newAccessToken, jwtProperties.getAccessTokenExpiration());
    }

    @Override
    @Transactional
    public void logout(String refreshTokenValue) {
        log.info("User logout attempt");

        RefreshToken storedToken = refreshTokenRepository.findByToken(refreshTokenValue)
                .orElseThrow(() -> new RefreshTokenNotFoundException(refreshTokenValue, true));

        storedToken.setRevoked(true);
        refreshTokenRepository.save(storedToken);

        log.info("User logged out successfully: userId={}", storedToken.getUser().getId());
    }

    private void saveRefreshToken(User user, String tokenValue) {
        RefreshToken refreshToken = RefreshToken.builder()
                .user(user)
                .token(tokenValue)
                .expiresAt(LocalDateTime.now().plusSeconds(jwtProperties.getRefreshTokenExpiration() / 1000))
                .revoked(false)
                .build();

        refreshTokenRepository.save(refreshToken);
    }
}