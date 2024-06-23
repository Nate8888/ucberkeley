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
            latitude: 37.78825,
            longitude: -122.4324,
            latitudeDelta: 0.0922,
            longitudeDelta: 0.0421,
          }}
        >
          <Circle
            center={{ latitude: 37.78825, longitude: -122.4324 }}
            radius={1000} // Radius in meters
            strokeColor="rgba(0, 0, 255, 0.5)" // Outline color
            fillColor="rgba(0, 0, 255, 0.1)" // Fill color
          />
          <Marker
            coordinate={{ latitude: 37.78825, longitude: -122.4324 }}
            onPress={handleMarkerPress}
          >
            <View style={styles.calloutView}>
              <Text style={styles.calloutText}>This is a circle range</Text>
            </View>
          </Marker>
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
  },
  calloutText: {
    fontSize: 14,
    color: 'black',
  },
});
