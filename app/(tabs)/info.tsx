import Ionicons from '@expo/vector-icons/Ionicons';
import { StyleSheet, View, StatusBar, ScrollView, TouchableOpacity, Text } from 'react-native';
import { useState } from 'react';

import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';

const CollapsibleSection = ({ title, children }) => {
  const [collapsed, setCollapsed] = useState(true);

  return (
    <View style={styles.collapsibleSection}>
      <TouchableOpacity onPress={() => setCollapsed(!collapsed)}>
        <ThemedText type="subtitle" style={styles.sectionTitle}>
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
      <ThemedText type="title" style={styles.mainHeader}>Know about what's happening.</ThemedText>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <CollapsibleSection title="Disaster">
          <Text style={styles.bullet}>• Details about the disaster</Text>
          <Text style={styles.bullet}>• More details</Text>
        </CollapsibleSection>
        <CollapsibleSection title="What is impacted">
          <Text style={styles.bullet}>• Description of impacted areas</Text>
          <Text style={styles.bullet}>• More impacted details</Text>
        </CollapsibleSection>
        <CollapsibleSection title="Ideas to overcome">
          <Text style={styles.bullet}>• Suggested actions to take</Text>
          <Text style={styles.bullet}>• Additional suggestions</Text>
        </CollapsibleSection>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f0f0f0', // Consistent background color
    padding: 16,
    paddingTop: StatusBar.currentHeight + 100, // Push down the content more
  },
  mainHeader: {
    textAlign: 'center',
    marginBottom: 60, // Move down the main header
    color: 'black', // Set the title color to black
    fontSize: 32, // Match the font size of "What's up, Nate 👋"
    fontWeight: 'bold', // Make the main header bold
  },
  scrollContent: {
    flexGrow: 1,
    justifyContent: 'flex-start', // Start from the top
    alignItems: 'center',
  },
  collapsibleSection: {
    width: '100%',
    marginBottom: 16,
    padding: 16,
    backgroundColor: '#fff',
    borderRadius: 8,
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  sectionTitle: {
    fontSize: 18,
    marginBottom: 8,
    fontWeight: 'bold',
    color: '#333', // Darker color for section titles
  },
  collapsibleContent: {
    paddingLeft: 16,
  },
  bullet: {
    fontSize: 16,
    marginBottom: 4,
    color: '#666', // Slightly darker gray for bullets
  },
});
