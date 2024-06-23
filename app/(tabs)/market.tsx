import { useState } from 'react';
import { StyleSheet, Platform, View, StatusBar, Dimensions, TouchableOpacity, Text } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';

const CollapsibleBox = ({ title, children }) => {
  const [collapsed, setCollapsed] = useState(true);

  return (
    <View style={styles.box}>
      <TouchableOpacity onPress={() => setCollapsed(!collapsed)}>
        <ThemedText type="subtitle" style={styles.boxTitle}>
          {title} <Ionicons name={collapsed ? 'chevron-down' : 'chevron-up'} size={16} />
        </ThemedText>
      </TouchableOpacity>
      {!collapsed && <View style={styles.collapsibleContent}>{children}</View>}
    </View>
  );
};

export default function TabTwoScreen() {
  return (
    <View style={styles.container}>
      <View style={styles.headerContainer}>
        <ThemedText type="title" style={styles.mainTitle}>Object</ThemedText>
      </View>
      <View style={styles.boxContainer}>
        <View style={styles.row}>
          <CollapsibleBox title="Disaster Event">
            <Text style={styles.bullet}>• Details about the disaster</Text>
            <Text style={styles.bullet}>• More details</Text>
          </CollapsibleBox>
          <CollapsibleBox title="Markets Impacted">
            <Text style={styles.bullet}>• Market 1</Text>
            <Text style={styles.bullet}>• Market 2</Text>
          </CollapsibleBox>
        </View>
        <View style={styles.row}>
          <CollapsibleBox title="Potential Companies Impacted">
            <Text style={styles.bullet}>• Company 1</Text>
            <Text style={styles.bullet}>• Company 2</Text>
          </CollapsibleBox>
          <CollapsibleBox title="Suggested Actions">
            <Text style={styles.bullet}>• Action 1</Text>
            <Text style={styles.bullet}>• Action 2</Text>
          </CollapsibleBox>
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
  headerContainer: {
    marginBottom: 20, // Adjust margin to move the title down
  },
  mainTitle: {
    textAlign: 'center',
    marginBottom: 20, // Increased margin to ensure visibility
    color: 'black', // Set the title color to black
    fontSize: 32, // Match the font size of "What's up, Nate 👋"
    fontWeight: 'bold', // Make the main header bold
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
  collapsibleContent: {
    paddingTop: 10,
  },
  bullet: {
    fontSize: 16,
    marginBottom: 4,
    color: '#666', // Slightly darker gray for bullets
  },
});
