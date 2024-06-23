import Ionicons from '@expo/vector-icons/Ionicons';
import { StyleSheet, View, StatusBar, ScrollView } from 'react-native';

import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';

export default function TabTwoScreen() {
  return (
    <View style={styles.container}>
      <ThemedText type="title" style={styles.mainHeader}>Know about what's happening.</ThemedText>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <ThemedText style={styles.text}>Disaster:</ThemedText>
        <ThemedText style={styles.text}>What is impacted:</ThemedText>
        <ThemedText style={styles.text}>Ideas to overcome:</ThemedText>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#d0d0d0', // Consistent background color
    padding: 16,
    paddingTop: StatusBar.currentHeight + 60, // Push down the content more
  },
  mainHeader: {
    textAlign: 'center',
    marginBottom: 20,
    color: 'black', // Set the title color to black
  },
  scrollContent: {
    flexGrow: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  text: {
    marginBottom: 16,
  },
});
