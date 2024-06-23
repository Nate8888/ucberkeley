import { StyleSheet, Platform, View, StatusBar, Dimensions } from 'react-native';
import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';

export default function TabTwoScreen() {
  return (
    <View style={styles.container}>
      <ThemedText type="title" style={styles.mainTitle}>Object</ThemedText>
      <View style={styles.boxContainer}>
        <View style={styles.row}>
          <View style={styles.box}>
            <ThemedText type="subtitle" style={styles.boxTitle}>Disaster Event</ThemedText>
          </View>
          <View style={styles.box}>
            <ThemedText type="subtitle" style={styles.boxTitle}>Markets Impacted</ThemedText>
          </View>
        </View>
        <View style={styles.row}>
          <View style={styles.box}>
            <ThemedText type="subtitle" style={styles.boxTitle}>Potential Companies Impacted</ThemedText>
          </View>
          <View style={styles.box}>
            <ThemedText type="subtitle" style={styles.boxTitle}>Suggested Actions</ThemedText>
          </View>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#d0d0d0', // Consistent background color
    padding: 16,
    paddingTop: StatusBar.currentHeight + 20, // Push down the content
  },
  mainTitle: {
    textAlign: 'center',
    marginBottom: 30, // Increased margin to ensure visibility
    backgroundColor: '#d0d0d0', // Ensure background color consistency
    color: 'black', // Set the title color to black
  },
  boxContainer: {
    flex: 1,
    justifyContent: 'center',
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  box: {
    backgroundColor: '#ffffff',
    width: (Dimensions.get('window').width / 2) - 24, // Adjust width to be half of the screen minus margins
    height: (Dimensions.get('window').width / 2) - 24, // Make height equal to width for square shape
    padding: 16,
    borderRadius: 8,
    shadowColor: '#000',
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 2,
    justifyContent: 'center',
    alignItems: 'center',
  },
  boxTitle: {
    textAlign: 'center',
  },
});
