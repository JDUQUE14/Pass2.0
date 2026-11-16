import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  StatusBar,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
} from 'react-native';
import * as LocalAuthentication from 'expo-local-authentication';
import { colors } from '../styles/theme';
import { createAccessLog } from '../services/api';

export default function DetalleNFC({ route, navigation }) {
  const { carnet } = route.params || {};
  const [transmitting, setTransmitting] = useState(false);

  // Función que maneja la autenticación biométrica antes del NFC
  const handleStartNFC = async () => {
    try {
      const hasHardware = await LocalAuthentication.hasHardwareAsync();
      const isEnrolled = await LocalAuthentication.isEnrolledAsync();

      if (!hasHardware || !isEnrolled) {
        Alert.alert(
          'Aviso Biometría',
          'Este dispositivo no tiene huella/rostro configurado. Se omitirá el paso biométrico para fines de prueba.',
          [{ text: 'Continuar', onPress: executeNfcTransmission }]
        );
        return;
      }

      const authResult = await LocalAuthentication.authenticateAsync({
        promptMessage: 'Autentícate para transmitir credencial NFC',
        fallbackLabel: 'Usar contraseña',
        cancelLabel: 'Cancelar',
      });

      if (authResult.success) {
        executeNfcTransmission();
      } else {
        Alert.alert('Autenticación fallida', 'No se pudo verificar tu identidad. Transmisión cancelada.');
      }
    } catch (error) {
      console.log('Error en biometría:', error);
      Alert.alert('Error', 'Ocurrió un error al intentar validar la biometría.');
    }
  };

  // Función que simula la transmisión NFC y guarda en el backend
  const executeNfcTransmission = () => {
    setTransmitting(true);

    setTimeout(async () => {
      setTransmitting(false);

      const logData = {
        location: `Torniquete - ${carnet?.institution_name || 'General'}`,
        status: 'Exitoso',
        card_id: carnet?.id,
      };

      try {
        await createAccessLog(logData);
      } catch (error) {
        console.log('No se pudo registrar el acceso en el servidor:', error);
      }

      Alert.alert(
        'Acceso Concedido',
        `Credencial "${carnet?.card_number || 'N/A'}" transmitida con éxito al lector NFC.`,
        [{ text: 'OK' }]
      );
    }, 3000);
  };

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor={colors.background} />

      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity
          onPress={() => navigation.goBack()}
          style={styles.backButton}
        >
          <Text style={styles.backText}>← Volver</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Credencial Digital</Text>
        <View style={{ width: 60 }} />
      </View>

      {/* Contenedor posicionado en la parte superior */}
      <View style={styles.mainContent}>
        <View style={styles.idCard}>
          {/* Avatar a la mitad del borde superior */}
          <View style={styles.avatarContainer}>
            <Text style={styles.avatarIcon}>👤</Text>
          </View>

          <View style={styles.infoSection}>
            <Text style={styles.label}>NOMBRE</Text>
            <Text style={styles.valueName}>Juan Jose Castro Duque</Text>

            <Text style={styles.label}>ROL</Text>
            <Text style={styles.valueRole}>{carnet?.role || 'Estudiante'}</Text>

            <Text style={styles.label}>INSTITUCIÓN</Text>
            <Text style={styles.valueInstitution}>{carnet?.institution_name || 'Institución Universitaria'}</Text>

            <Text style={styles.label}>NÚMERO DE CARNET</Text>
            <Text style={styles.valueCardNumber}>{carnet?.card_number || '00000000'}</Text>
          </View>

          {/* Botón NFC en la parte inferior de la tarjeta */}
          <TouchableOpacity
            style={[styles.actionButton, transmitting && styles.actionButtonDisabled]}
            onPress={handleStartNFC}
            disabled={transmitting}
            activeOpacity={0.8}
          >
            {transmitting ? (
              <View style={styles.buttonLoadingRow}>
                <ActivityIndicator size="small" color="#FFFFFF" style={{ marginRight: 8 }} />
                <Text style={styles.actionButtonText}>TRANSMITIENDO...</Text>
              </View>
            ) : (
              <Text style={styles.actionButtonText}>📶 BOTÓN NFC</Text>
            )}
          </TouchableOpacity>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
    paddingTop: 45,
    paddingHorizontal: 20,
    paddingBottom: 25,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  backButton: {
    paddingVertical: 8,
    paddingRight: 12,
  },
  backText: {
    color: colors.primary,
    fontSize: 15,
    fontWeight: '600',
  },
  headerTitle: {
    color: colors.textPrimary,
    fontSize: 16,
    fontWeight: 'bold',
  },
  mainContent: {
    width: '100%',
    alignItems: 'center',
    marginTop: 20, // Ubica la credencial en la parte superior limpia
  },
  idCard: {
    width: '100%',
    backgroundColor: colors.surface,
    borderRadius: 24,
    borderWidth: 1.5,
    borderColor: colors.surfaceBorder,
    marginTop: 55, // Espacio para que el avatar montado no se corte con la parte superior
    paddingTop: 65,
    paddingHorizontal: 24,
    paddingBottom: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.25,
    shadowRadius: 10,
    elevation: 6,
  },
  avatarContainer: {
    width: 110,
    height: 110,
    borderRadius: 55,
    backgroundColor: colors.surface,
    borderWidth: 2.5,
    borderColor: colors.surfaceBorder,
    justifyContent: 'center',
    alignItems: 'center',
    position: 'absolute',
    top: -55, // La mitad exacta fuera y la mitad dentro
    alignSelf: 'center',
    zIndex: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 5,
    elevation: 8,
  },
  avatarIcon: {
    fontSize: 50,
  },
  infoSection: {
    marginBottom: 24,
  },
  label: {
    color: colors.textSecondary,
    fontSize: 10,
    fontWeight: '700',
    letterSpacing: 1.2,
    marginTop: 10,
    marginBottom: 2,
  },
  valueName: {
    color: colors.textPrimary,
    fontSize: 18,
    fontWeight: 'bold',
  },
  valueRole: {
    color: colors.primary,
    fontSize: 15,
    fontWeight: '600',
  },
  valueInstitution: {
    color: colors.textPrimary,
    fontSize: 14,
    fontWeight: '500',
  },
  valueCardNumber: {
    color: colors.textSecondary,
    fontSize: 13,
    fontWeight: '500',
  },
  actionButton: {
    backgroundColor: colors.primary,
    paddingVertical: 16,
    borderRadius: 14,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 6,
    elevation: 4,
  },
  actionButtonDisabled: {
    opacity: 0.7,
  },
  buttonLoadingRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  actionButtonText: {
    color: '#FFFFFF',
    fontWeight: 'bold',
    fontSize: 15,
    letterSpacing: 0.8,
  },
});