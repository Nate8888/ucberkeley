import React, { useState } from 'react';
import { StyleSheet, View, ScrollView, StatusBar, Dimensions, Text } from 'react-native';
import MapView, { Marker, Circle } from 'react-native-maps';

import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';

export default function ExploreScreen() {
  const [selectedLocation, setSelectedLocation] = useState(null);

  const handleMarkerPress = () => {
    setSelectedLocation({
      latitude: 37.78825,
      longitude: -122.4324,
    });
  };

  const generateRandomUSCoordinates = () => {
    const latMin = 24.396308; // Southernmost point in the continental U.S.
    const latMax = 49.384358; // Northernmost point in the continental U.S.
    const lonMin = -125.0; // Westernmost point in the continental U.S.
    const lonMax = -66.93457; // Easternmost point in the continental U.S.
  
    const latitude = Math.random() * (latMax - latMin) + latMin;
    const longitude = Math.random() * (lonMax - lonMin) + lonMin;
    return { latitude, longitude };
  };
  
  const sampleCircles = Array.from({ length: 50 }, () => generateRandomUSCoordinates());

  return (
    <View style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContainer}>
        <ThemedView style={styles.titleContainer}>
          <ThemedText type="title">Explore</ThemedText>
        </ThemedView>
        <ThemedText style={styles.subtitle}>See where distress is around the world.</ThemedText>
        <MapView
          style={styles.map}
          initialRegion={{
            latitude: 37.0902,
            longitude: -95.7129,
            latitudeDelta: 100,
            longitudeDelta: 100,
          }}
        >
{sampleCircles.map((circle, index) => (
        <Circle
          key={index}
          center={circle}
          radius={100000} // Radius in meters, adjust as needed
          strokeColor="rgba(255, 0, 0, 0.5)" // Red outline color
          fillColor="rgba(255, 0, 0, 0.2)" // Red fill color
        />
      ))}
        </MapView>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f0f0f0', // Consistent background color
  },
  scrollContainer: {
    flexGrow: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingTop: StatusBar.currentHeight + 20,
    paddingBottom: 20,
  },
  titleContainer: {
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 40, // Move down the title text
    paddingVertical: 10,
    backgroundColor: '#f0f0f0', // Consistent background color
  },
  subtitle: {
    fontSize: 18,
    textAlign: 'center',
    marginVertical: 10,
    backgroundColor: '#f0f0f0', // Consistent background color
  },
  map: {
    width: Dimensions.get('window').width,
    height: Dimensions.get('window').height * 0.7,
  },
  calloutView: {
    padding: 5,
    backgroundColor: '#f0f0f0', // Consistent background color
    borderRadius: 5,
    borderColor: 'black',
    borderWidth: 1,
    shadowColor: '#000',
    shadowOpacity: 0.3,
    shadowRadius: 5,
    elevation: 5,
    marginBottom: 100,
  },
  calloutText: {
    fontSize: 14,
    color: 'black',
  },
});
