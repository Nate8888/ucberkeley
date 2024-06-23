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
        <ThemedText type="subtitle" style={styles.sectionTitle}>{title}</ThemedText>
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
    backgroundColor: '#d0d0d0', // Consistent background color
    padding: 16,
    paddingTop: StatusBar.currentHeight + 80, // Push down the content more
  },
  mainHeader: {
    textAlign: 'center',
    marginBottom: 40, // Move down the main header
    color: 'black', // Set the title color to black
  },
  scrollContent: {
    flexGrow: 1,
    justifyContent: 'flex-start', // Start from the top
    alignItems: 'center',
  },
  collapsibleSection: {
    width: '100%',
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 18,
    marginBottom: 8,
  },
  collapsibleContent: {
    paddingLeft: 16,
  },
  bullet: {
    fontSize: 16,
    marginBottom: 4,
  },
});
